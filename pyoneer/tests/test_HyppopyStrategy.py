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

import os
import shutil
import unittest

from avid.selectors.keyValueSelector import ActionTagSelector
from pyoneer.criteria.durationCriterion import DurationCriterion
from pyoneer.criteria.propertyCriterion import PropertyCriterion
from pyoneer.evaluation import EvaluationStrategy
from pyoneer.evaluationResult import readOptimizationResult
from pyoneer.metrics import DefaultMetric
from pyoneer.optimization.hyppopyStrategy import HyppopyGridSearchStrategy
from pyoneer.optimization.strategy import detectOptimizationStrategies
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

class DummyOptimizationStrategy(HyppopyGridSearchStrategy):

    def defineSearchParameters(self):
        desc = param_helper.generateDescriptor(['x','delay'])
        param_helper.decorateParameter(desc, 'x', minimum=-100, maximum=200, frequency = 4, domain = 'uniform', type = 'float')
        param_helper.decorateParameter(desc, 'delay', minimum=-5, maximum=10, frequency = 4, domain = 'uniform', type = 'float')

        return desc

    def defineName(self):
        return "TestOptimization"

class TestOptimizationStrategy(unittest.TestCase):
  def setUp(self):

    self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "workflow")
    self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "workflow", "testworkflow_artefacts"+os.extsep+"avid")
    self.tempDir = os.path.join(os.path.split(__file__)[0],"temporary")
    self.sessionDir = os.path.join(self.tempDir, "test_EvaluationStrategy")
    self.testWorkflowFile = os.path.join(os.path.split(__file__)[0],"data", "workflow", "testworkflow"+os.extsep+"py")
    self.testResultFile = os.path.join(os.path.split(__file__)[0],"data", "optimizationStrategy", "result"+os.extsep+"opt")

  def tearDown(self):
    try:
      shutil.rmtree(self.tempDir)
    except:
      pass

  def test_Optimization(self):
    strat = DummyOptimizationStrategy(__file__, self.sessionDir)

    result = strat.optimize(workflowFile=self.testWorkflowFile, artefactFile=self.testArtefactFile)

    self.assertTrue(not result is None)
    self.assertEqual(strat.defineName(), result.name)

    best = result.best[0]
    self.assertEqual('Best',best.label)
    refParameter = {'delay': 0, 'x': 100}
    refSVMeasure = 0.0
    self.assertEqual(refParameter, best.workflowModifier)
    self.assertAlmostEqual(refSVMeasure, best.svMeasure, 6)

    loadedResult = readOptimizationResult(self.testResultFile)
    self.assertEqual(self.testArtefactFile, result.artefactFile)
    self.assertEqual(self.testWorkflowFile, result.workflowFile)
    self.assertEqual(loadedResult.valueDescriptions, result.valueDescriptions)
    self.assertEqual(loadedResult.valueNames, result.valueNames)
    self.assertEqual(loadedResult.name, result.name)
    self.assertEqual(len(loadedResult.best), len(result.best))
    self.assertEqual(len(loadedResult.candidates), len(result.candidates))


if __name__ == '__main__':
    unittest.main()