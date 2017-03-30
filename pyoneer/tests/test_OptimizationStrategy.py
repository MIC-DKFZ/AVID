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
from pyoneer.evaluationResult import loadEvaluationResult
from pyoneer.metrics import DefaultMetric
from pyoneer.opitmizers.exhaustiveSearch import ExhaustiveSearchOptimizer
from pyoneer.optimization import OptimizationStrategy, detectOptimizationStrategies


class DummyEvalStrategy(EvaluationStrategy):

    def defineMetric(self):
        '''This method must be implemented and return an metric instance.'''
        return DefaultMetric([DurationCriterion(), PropertyCriterion('myValue', ActionTagSelector('Result'))],
                             self.sessionDir,
                             measureWeights={'pyoneer.criteria.PropertyCriterion.myValue.mean':1, 'pyoneer.criteria.DurationCriterion.duration.mean':1},
                             clearSessionDir=self.clearSessionDir)
    def defineName(self):
        return "TestEvaluation"

class DummyOptimizationStrategy(OptimizationStrategy):

    def defineOptimizer(self):
        '''This method must be implemented and return an metric instance.'''
        return ExhaustiveSearchOptimizer(['x','delay'], [-200,-10], [200,10],[4,4])

    def defineName(self):
        return "TestOptimization"

class TestOptimizationStrategy(unittest.TestCase):
  def setUp(self):

    self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "workflow")
    self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "workflow", "testworkflow_artefacts"+os.extsep+"avid")
    self.tempDir = os.path.join(os.path.split(__file__)[0],"temporary")
    self.sessionDir = os.path.join(self.tempDir, "test_EvaluationStrategy")
    self.testWorkflowFile = os.path.join(os.path.split(__file__)[0],"data", "workflow", "testworkflow"+os.extsep+"py")

  def tearDown(self):
    try:
      shutil.rmtree(self.tempDir)
    except:
      pass

  def test_Optimization(self):
    strat = DummyOptimizationStrategy(__file__, self.sessionDir)

    results = strat.optimize(workflowFile=self.testWorkflowFile, artefactFile=self.testArtefactFile)

    self.assert_(not results is None)
    result = results.itervalues().next()
    refParameter = {'delay': 0, 'x': 100}
    refSVMeasure = 0.0
    self.assertEqual(refParameter, result[0])
    self.assertAlmostEquals(refSVMeasure, result[1].svMeasure, 6)

  def test_StrategyDetection(self):
    stratClasses = detectOptimizationStrategies(__file__)

    self.assertEqual(len(stratClasses), 1)
    self.assertEqual(stratClasses[0].__name__, 'DummyOptimizationStrategy')
    strat = stratClasses[0](__file__, self.sessionDir)
    self.assertEqual(strat.defineName(), 'TestOptimization')


if __name__ == '__main__':
    unittest.main()