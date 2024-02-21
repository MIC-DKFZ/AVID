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

import pyoneer.evaluationResult as EvalResults
from pyoneer.evaluation import EvalInstanceDescriptor


class TestEvaluationResults(unittest.TestCase):
  def setUp(self):

    self.testDataDir = os.path.join(os.path.split(__file__)[0],"data")
    self.testResultFile = os.path.join(os.path.split(__file__)[0],"data",'evaluationResults', "result"+os.extsep+"eval")
    self.testResultDefaultFile = os.path.join(os.path.split(__file__)[0],"data",'evaluationResults', "result_default"+os.extsep+"eval")
    self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary", "test_evaluationResults")
    self.testWorkflowFile = os.path.join(os.path.split(__file__)[0],"data", "metricsTest", "testworkflow"+os.extsep+"py")

    self.refMeasurements = {'crit1':1, 'crit2':0.5}
    self.refInstanceMeasurements = { EvalInstanceDescriptor({'case':'C1'}, 'testID'): {'crit1.1': 0.1, 'crit2.1': 0.2}}
    self.refWeights = {'crit1': 0.5, 'crit2':0.7}
    self.refWorkflowModifier={'mod1': 'm1', 'mod2':'m2'}


    self.refEvalResult = EvalResults.EvaluationResult(self.refMeasurements, self.refInstanceMeasurements,
                                                      workflowModifier=self.refWorkflowModifier,
                                                      measureWeights = self.refWeights, name='TestEval',
                                                      workflowFile='myWorkflow', artefactFile='myArtefacts',
                                                      valueNames={'vn1':'a'}, valueDescriptions={'vd1':'description'})

    self.refMeasurements2 = {'crit1':3, 'crit2':42}
    self.refInstanceMeasurements2 = { EvalInstanceDescriptor({'case':'C1'}, 'testID'): {'crit1.1': 1.1, 'crit2.1': 2.2}}
    self.refWeights2 = {'crit1': 0.2, 'crit2':2}
    self.refWorkflowModifier2={'mod1': 'm11', 'mod2':'m22'}
    self.candidateResult2 = EvalResults.MeasurementResult(self.refMeasurements2,self.refInstanceMeasurements2,"Cand2",self.refWorkflowModifier2,self.refWeights2)

    self.refMeasurements3 = {'crit1':0.1, 'crit2':0.001}
    self.refInstanceMeasurements3 = { EvalInstanceDescriptor({'case':'C1'}, 'testID'): {'crit1.1': 11.1, 'crit2.1': 22.2}}
    self.refWeights3 = {'crit1': 1, 'crit2':1}
    self.refWorkflowModifier3={'mod1': 'm111', 'mod2':'m222'}
    self.candidateResult3 = EvalResults.MeasurementResult(self.refMeasurements3,self.refInstanceMeasurements3,"Cand3",self.refWorkflowModifier3,self.refWeights3)

    self.testOptResultFile = os.path.join(os.path.split(__file__)[0],"data",'evaluationResults', "result"+os.extsep+"opt")
    self.testOptResultDefaultFile = os.path.join(os.path.split(__file__)[0],"data",'evaluationResults', "result_default"+os.extsep+"opt")

    self.refOptResult = EvalResults.OptimizationResult(name='test_optimization', workflowFile='myWorkflow',artefactFile='myArtefacts')
    self.refOptResult.append(self.refEvalResult)
    self.refOptResult.append(self.candidateResult2)
    self.refOptResult.append(self.candidateResult3, label='winner', asBest=True)

  def tearDown(self):
    try:
      shutil.rmtree(self.sessionDir)
    except:
      pass

  def assert_file_content(self, filePathTest, filePathRef):
    with open(filePathRef) as refF:
      with open(filePathTest) as testF:
        ref = refF.read()
        test = testF.read()

        self.assertEqual(ref, test)

  def test_EvaluationResult_load(self):

    loadedResult = EvalResults.readEvaluationResult(self.testResultFile)
    self.assertEqual(self.refEvalResult.artefactFile, loadedResult.artefactFile)
    self.assertEqual(self.refEvalResult.workflowFile, loadedResult.workflowFile)
    self.assertEqual(self.refEvalResult.valueDescriptions, loadedResult.valueDescriptions)
    self.assertEqual(self.refEvalResult.valueNames, loadedResult.valueNames)
    self.assertEqual(self.refEvalResult.measurements, loadedResult.measurements)
    self.assertEqual(self.refEvalResult.workflowModifier, loadedResult.workflowModifier)
    self.assertEqual(self.refEvalResult.measureWeights, loadedResult.measureWeights)

  def test_EvaluationResult_save(self):
    testFilePath = os.path.join(self.sessionDir, 'result'+os.extsep+'eval')
    testFileDefaultPath = os.path.join(self.sessionDir, 'result_default'+os.extsep+'eval')

    EvalResults.writeEvaluationResult(testFilePath, self.refEvalResult)
    self.assert_file_content(testFilePath, self.testResultFile)

    refResultDefaults = EvalResults.EvaluationResult(dict(),dict())
    EvalResults.writeEvaluationResult(testFileDefaultPath, refResultDefaults)
    self.assert_file_content(testFileDefaultPath, self.testResultDefaultFile)

  def test_OptimizationResult_save(self):
    testFilePath = os.path.join(self.sessionDir, 'result'+os.extsep+'opt')
    testFileDefaultPath = os.path.join(self.sessionDir, 'result_default'+os.extsep+'opt')

    EvalResults.writeOptimizationResult(testFilePath, self.refOptResult)
    self.assert_file_content(testFilePath, self.testOptResultFile)

    refResultDefaults = EvalResults.OptimizationResult()
    EvalResults.writeOptimizationResult(testFileDefaultPath, refResultDefaults)
    self.assert_file_content(testFileDefaultPath, self.testOptResultDefaultFile)


if __name__ == '__main__':
    unittest.main()