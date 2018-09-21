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
import shutil
import unittest

from avid.selectors.keyValueSelector import ActionTagSelector
from pyoneer.criteria.durationCriterion import DurationCriterion
from pyoneer.criteria.propertyCriterion import PropertyCriterion
from pyoneer.evaluation import EvaluationStrategy
from pyoneer.evaluationResult import readOptimizationResult
from pyoneer.metrics import DefaultMetric
from pyoneer.optimization.exhaustiveSearchStrategy import ExhaustiveSearchStrategy
from pyoneer.optimization.strategy import detectOptimizationStrategies
import pyoneer.optimization.parameters as param_helper

class DummyEvalStrategy(EvaluationStrategy):

    def defineMetric(self):
        '''This method must be implemented and return an metric instance.'''
        return DefaultMetric([DurationCriterion(), PropertyCriterion('myValue', ActionTagSelector('Result'))],
                             self.sessionDir,
                             measureWeights={'pyoneer.criteria.PropertyCriterion.myValue.mean':1},
                             clearSessionDir=self.clearSessionDir)
    def defineName(self):
        return "TestEvaluation"

class DummyOptimizationStrategy(ExhaustiveSearchStrategy):

    def defineSearchParameters(self):
        desc = param_helper.generateDescriptor(['x'])
        param_helper.decorateParameter(desc, 'x', minimum=-200, maximum=200)
        param_helper.decorateCustom(desc, 'x', 'frequency', 5)
        return desc

    def defineName(self):
        return "TestOptimization"

    def defineStaticWorkflowModifier(self, candidateSearchParameter = None):
        result = dict()
        result['delay'] = 9999
        if candidateSearchParameter is not None:
            result['delay'] = candidateSearchParameter['x']*2
        return result

class TestOptimizationStrategyStatic(unittest.TestCase):
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
    refParameter = {'delay':200, 'x': 100}
    refSVMeasure = 0.0
    self.assertEqual(refParameter, best.workflowModifier)
    self.assertAlmostEqual(refSVMeasure, best.svMeasure, 6)


if __name__ == '__main__':
    unittest.main()