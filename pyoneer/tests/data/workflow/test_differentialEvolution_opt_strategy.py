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

from avid.selectors.keyValueSelector import ActionTagSelector
from pyoneer.criteria.durationCriterion import DurationCriterion
from pyoneer.criteria.propertyCriterion import PropertyCriterion
from pyoneer.evaluation import EvaluationStrategy
from pyoneer.metrics import DefaultMetric
from pyoneer.optimization.differentialEvolutionStrategy import DefaultDifferentialEvolutionStrategy
import pyoneer.optimization.parameters as param_helper

class DummyEvalStrategy(EvaluationStrategy):

    def defineMetric(self):
        '''This method must be implemented and return an metric instance.'''
        return DefaultMetric([DurationCriterion(), PropertyCriterion('myValue', ActionTagSelector('Result'))],
                             self.sessionDir,
                             measureWeights={'pyoneer.criteria.PropertyCriterion.myValue.mean':1, 'pyoneer.criteria.DurationCriterion.duration.mean':1},
                             clearSessionDir=self.clearSessionDir)
    def defineName(self):
        return "TestEvaluation"

class DummyOptimizationStrategy(DefaultDifferentialEvolutionStrategy):

    def defineSearchParameters(self):
        desc = param_helper.generateDescriptor(['x','delay'])
        param_helper.decorateMinimum(desc, 'x', -200)
        param_helper.decorateMinimum(desc, 'delay', -10)
        param_helper.decorateMaximum(desc, 'x', 200)
        param_helper.decorateMaximum(desc, 'delay', 10)
        return desc

    def defineName(self):
        return "TestDifferentialEvolutionOptimization"
