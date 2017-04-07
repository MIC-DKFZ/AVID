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

    self.refResult = EvalResults.EvaluationResult(self.refMeasurements, self.refInstanceMeasurements,
                                                  workflowModifier={'mod1': 'm1', 'mod2':'m2'},
                                                  measureWeights = self.refWeights, name='TestEval',
                                                  workflowFile='myWorkflow', artefactFile='myArtefacts',
                                                  valueNames={'vn1':'a'}, valueDescriptions={'vd1':'description'})

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
    self.assertEqual(self.refResult.artefactFile, loadedResult.artefactFile)
    self.assertEqual(self.refResult.workflowFile, loadedResult.workflowFile)
    self.assertEqual(self.refResult.valueDescriptions, loadedResult.valueDescriptions)
    self.assertEqual(self.refResult.valueNames, loadedResult.valueNames)
    self.assertEqual(self.refResult.measurements, loadedResult.measurements)
    self.assertEqual(self.refResult.workflowModifier, loadedResult.workflowModifier)
    self.assertEqual(self.refResult.measureWeights, loadedResult.measureWeights)

  def test_EvaluationResult_save(self):
    testFilePath = os.path.join(self.sessionDir, 'result'+os.extsep+'eval')
    testFileDefaultPath = os.path.join(self.sessionDir, 'result_default'+os.extsep+'eval')

    EvalResults.writeEvaluationResult(testFilePath, self.refResult)
    self.assert_file_content(testFilePath, self.testResultFile)

    refResultDefaults = EvalResults.EvaluationResult(dict(),dict())
    EvalResults.writeEvaluationResult(testFileDefaultPath, refResultDefaults)
    self.assert_file_content(testFileDefaultPath, self.testResultDefaultFile)


if __name__ == '__main__':
    unittest.main()