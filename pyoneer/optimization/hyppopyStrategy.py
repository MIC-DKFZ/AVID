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

from pyoneer.optimization.hyppopyWrapper import HyppopyOptimizer
from pyoneer.optimization.strategy import OptimizationStrategy


class HyppopyPoolStrategy(OptimizationStrategy):
    ''' Base class for strategies that uses hyppopy (and its solver pool) to optimize a workflow.
        Implement defineSearchParameters() to generate the "hyperparameter" section of the hyppopy
        config dict.
        Implement defineSolverSettings() to generate the "settings" section of the hyppopy
        config dict.
    '''

    def defineSolverSettings(self):
        '''Returns the "settings" section/sub dict of the hyppopy config dict. This result will be used to properly
        configure the solver.
        '''
        raise NotImplementedError('Reimplement in derived class to function correclty')

    def defineOptimizer(self):

        params = self.defineSearchParameters()

        config = {"hyperparameter" : params,
                  "settings" : self.defineSolverSettings()}

        return HyppopyOptimizer(parameterIDs=list(params.keys()), config=config)

    def defineName(self):
        return "HyppopyPoolStrategy"


class HyppopyGridSearchStrategy(HyppopyPoolStrategy):
    ''' Class for strategies that uses hyppopy (and its solver pool) to optimize a workflow via gridsearch.
        Implement defineSearchParameters() to generate the "hyperparameter" section of the hyppopy
        config dict.
        Reimplement defineSolverSettings() to generate the "settings" section of the hyppopy
        config dict.
    '''

    def defineSolverSettings(self):
        '''Returns the "settings" section/sub dict of the hyppopy config dict. This result will be used to properly
        configure the solver.
        '''
        return {'custom':{'use_solver': 'gridsearch'}}

    def defineName(self):
        return "HyppopyGridSearchStrategy"

class HyppopyHyperoptStrategy(HyppopyPoolStrategy):
    ''' Class for strategies that uses hyppopy (and its solver pool) to optimize a workflow via Hyperopt.
        Implement defineSearchParameters() to generate the "hyperparameter" section of the hyppopy
        config dict.
        Reimplement defineSolverSettings() to generate the "settings" section of the hyppopy
        config dict.
    '''

    def defineSolverSettings(self):
        '''Returns the "settings" section/sub dict of the hyppopy config dict. This result will be used to properly
        configure the solver.
        '''
        return {'custom':{'use_solver': 'hyperopt'}}

    def defineName(self):
        return "HyppopyHyperoptStrategy"
