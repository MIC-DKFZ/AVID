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
import unittest

import shutil

from pyoneer.criteria.durationCriterion import DurationCriterion

from avid.selectors.keyValueSelector import ActionTagSelector
from pyoneer.criteria.propertyCriterion import PropertyCriterion
from pyoneer.evaluation import EvaluationStrategy, detectEvaluationStrategies
from pyoneer.evaluationResult import readEvaluationResult
from pyoneer.metrics import DefaultMetric


class DummyStrategy(EvaluationStrategy):

    def defineMetric(self):
        '''This method must be implemented and return an metric instance.'''
        return DefaultMetric([DurationCriterion(), PropertyCriterion('myValue', ActionTagSelector('Result'))],
                             self.sessionDir, clearSessionDir=self.clearSessionDir)

    def defineName(self):
        return "TestEvaluation"

class TestEvaluationStrategy(unittest.TestCase):
  def setUp(self):

    self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "workflow")
    self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "workflow", "testworkflow_artefacts"+os.extsep+"avid")
    self.tempDir = os.path.join(os.path.split(__file__)[0],"temporary")
    self.sessionDir = os.path.join(self.tempDir, "test_EvaluationStrategy")
    self.testWorkflowFile = os.path.join(os.path.split(__file__)[0],"data", "workflow", "testworkflow"+os.extsep+"py")
    self.maxDiff = None

  def tearDown(self):
    try:
      shutil.rmtree(self.tempDir)
    except:
      pass

  def assertDictEqual(self, d1, d2, msg=None):
    '''special implementation to compare with assertAlmostEqual, because measurements might differ slightly.'''
    for k,v1 in d1.items():
      self.assertIn(k, d2, msg)
      v2 = d2[k]
      self.assertAlmostEqual(v1, v2, 5, msg)
    return True

  def test_Evaluation(self):
    strat = DummyStrategy(self.sessionDir)

    result = strat.evaluate(artefactFile=self.testArtefactFile, workflowFile=self.testWorkflowFile)
    ref = readEvaluationResult(os.path.join(self.testDataDir, 'result.eval'))
    self.assertDictEqual(result.measurements, ref.measurements)

  def test_Evaluation_withModifier(self):
    strat = DummyStrategy(self.sessionDir)

    result = strat.evaluate(artefactFile=self.testArtefactFile, workflowFile=self.testWorkflowFile, workflowModifier={'x':50,'delay':42})
    ref = readEvaluationResult(os.path.join(self.testDataDir, 'result_with_modifier.eval'))
    self.assertDictEqual(result.measurements, ref.measurements)

  def test_StrategyDetection(self):
    stratClasses = detectEvaluationStrategies(__file__)

    self.assertEqual(len(stratClasses), 1)
    self.assertEqual(stratClasses[0].__name__, 'DummyStrategy')
    strat = stratClasses[0](self.sessionDir)
    self.assertEqual(strat.defineName(), 'TestEvaluation')


if __name__ == '__main__':
    unittest.main()