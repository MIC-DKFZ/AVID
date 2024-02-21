# SPDX-FileCopyrightText: 2024, German Cancer Research Center (DKFZ), Division of Medical Image Computing (MIC)
#
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# or find it in LICENSE.txt.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pyoneer.optimization.parameters as param_helper
from pyoneer.optimization.exhaustiveSearch import ExhaustiveSearchOptimizer
from pyoneer.optimization.strategy import OptimizationStrategy


class ExhaustiveSearchStrategy(OptimizationStrategy):
    ''' Predefined strategy that uses the exhaustive search optimization.
    This is more a demo strategy, because the optimization scheme is very inefficient.
    To use it you have to derive and implement defineSearchParameters. Additionally you have
    to decorate the parameter with 'frequency' to indicate the number of samples per parameters.
    '''

    def defineOptimizer(self):
        paramdesc = self.defineSearchParameters()

        names = list()
        minimas = list()
        maximas = list()
        freqs = list()

        for param in paramdesc:
            names.append(param)
            minimas.append(param_helper.getMinimum(paramdesc,param,True, scaleToOpt=True))
            maximas.append(param_helper.getMaximum(paramdesc,param,True, scaleToOpt=True))
            freqs.append(param_helper.getDecoration(paramdesc, param, 'frequency',True, scaleToOpt=True))

        return ExhaustiveSearchOptimizer(names, minimas, maximas,freqs)

    def defineName(self):
        return "ExhaustiveSearch"
