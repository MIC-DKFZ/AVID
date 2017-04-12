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

import subprocess

from avid.selectors.keyValueSelector import ActionTagSelector
from pyoneer.criteria.durationCriterion import DurationCriterion
from pyoneer.criteria.propertyCriterion import PropertyCriterion
from pyoneer.evaluation import EvaluationStrategy
from pyoneer.evaluationResult import readOptimizationResult, readEvaluationResult
from pyoneer.metrics import DefaultMetric
from pyoneer.optimization.exhaustiveSearchStrategy import ExhaustiveSearchStrategy
from pyoneer.optimization.strategy import detectOptimizationStrategies
import pyoneer.optimization.parameters as param_helper

class TestOptimizationStrategy(unittest.TestCase):
  def setUp(self):

    self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "workflow")
    self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "workflow", "testworkflow_artefacts"+os.extsep+"avid")
    self.testWorkflowFile = os.path.join(os.path.split(__file__)[0],"data", "workflow", "testworkflow"+os.extsep+"py")
    self.testEvalStratFile = os.path.join(os.path.split(__file__)[0],"data", "workflow", "test_eval_strategy"+os.extsep+"py")
    self.testOptStratFile = os.path.join(os.path.split(__file__)[0],"data", "workflow", "test_opt_strategy"+os.extsep+"py")
    self.tempDir = os.path.join(os.path.split(__file__)[0],"temporary")
    self.sessionDir = os.path.join(self.tempDir, "test_AvidPyoneer")
    self.testResultFile = os.path.join(os.path.split(__file__)[0],"data", "optimizationStrategy", "result"+os.extsep+"opt")

  def tearDown(self):
    try:
      shutil.rmtree(self.tempDir)
    except:
      pass

  def test_Optimize(self):
    resultPath = os.path.join(self.tempDir, "test_AvidPyoneer", "result"+os.extsep+"opt")

    clicall = 'avidpyoneer optimize "{}" "{}" -w "{}" -a "{}" -n AvidPyoneer_Test'.format(self.testOptStratFile, resultPath, self.testWorkflowFile, self.testArtefactFile)

    self.assertEquals(0, subprocess.call(clicall))

    result = readOptimizationResult(resultPath)
    self.assert_(not result is None)
    self.assertEquals('AvidPyoneer_Test', result.name)

    best = result.best[0]
    self.assertEqual('Best',best.label)
    refParameter = {'delay': '0', 'x': '100'}
    refSVMeasure = 0.0
    self.assertEqual(refParameter, best.workflowModifier)
    self.assertAlmostEquals(refSVMeasure, best.svMeasure, 6)

    loadedResult = readOptimizationResult(self.testResultFile)
    self.assertEqual(loadedResult.artefactFile, result.artefactFile)
    self.assertEqual(loadedResult.workflowFile, result.workflowFile)
    self.assertEqual(loadedResult.valueDescriptions, result.valueDescriptions)
    self.assertEqual(loadedResult.valueNames, result.valueNames)
    self.assertEqual(len(loadedResult.best), len(result.best))
    self.assertEqual(len(loadedResult.candidates), len(result.candidates))

  def test_Evaluate(self):
    resultPath = os.path.join(self.tempDir, "test_AvidPyoneer", "result"+os.extsep+"eval")

    clicall = 'avidpyoneer evaluate "{}" "{}" -w "{}" -a "{}" -n AvidPyoneer_Test'.format(self.testOptStratFile, resultPath, self.testWorkflowFile, self.testArtefactFile)

    self.assertEquals(0, subprocess.call(clicall))

    result = readEvaluationResult(resultPath)
    self.assert_(not result is None)
    self.assertEquals('AvidPyoneer_Test', result.name)


if __name__ == '__main__':
    unittest.main()