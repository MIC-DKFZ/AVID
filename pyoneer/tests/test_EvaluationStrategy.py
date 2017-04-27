# AVID - pyoneer
# AVID based tool for algorithmic evaluation and optimization
#
# Copyright (c) German Cancer Research Center,
# Software development for Integrated Diagnostic and Therapy (SIDT).
# All rights reserved.
#
# This software is distributed WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.
#
# See LICENSE.txt or http://www.dkfz.de/en/sidt/index.html for details.

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
    for k,v1 in d1.iteritems():
      self.assertIn(k, d2, msg)
      v2 = d2[k]
      self.assertAlmostEquals(v1, v2, 5, msg)
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