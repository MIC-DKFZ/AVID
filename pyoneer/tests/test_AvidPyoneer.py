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

import subprocess

from avid.common import osChecker
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
    self.useShell = not osChecker.isWindows()

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

    self.assertEqual(0, subprocess.call(clicall, shell= self.useShell))

    result = readOptimizationResult(resultPath)
    self.assertTrue(not result is None)
    self.assertEqual('AvidPyoneer_Test', result.name)

    best = result.best[0]
    self.assertEqual('Best',best.label)
    refParameter = {'delay': '0.0', 'x': '100.0'}
    refSVMeasure = 0.0
    self.assertEqual(refParameter, best.workflowModifier)
    self.assertAlmostEqual(refSVMeasure, best.svMeasure, 6)

    loadedResult = readOptimizationResult(self.testResultFile)
    self.assertEqual(self.testArtefactFile, result.artefactFile)
    self.assertEqual(self.testWorkflowFile, result.workflowFile)
    self.assertEqual(loadedResult.valueDescriptions, result.valueDescriptions)
    self.assertEqual(loadedResult.valueNames, result.valueNames)
    self.assertEqual(len(loadedResult.best), len(result.best))
    self.assertEqual(len(loadedResult.candidates), len(result.candidates))

  def test_Evaluate(self):
    resultPath = os.path.join(self.tempDir, "test_AvidPyoneer", "result"+os.extsep+"eval")

    clicall = 'avidpyoneer evaluate "{}" "{}" -w "{}" -a "{}" -n AvidPyoneer_Test'.format(self.testOptStratFile, resultPath, self.testWorkflowFile, self.testArtefactFile)

    self.assertEqual(0, subprocess.call(clicall, shell= self.useShell))

    result = readEvaluationResult(resultPath)
    self.assertTrue(not result is None)
    self.assertEqual('AvidPyoneer_Test', result.name)


if __name__ == '__main__':
    unittest.main()