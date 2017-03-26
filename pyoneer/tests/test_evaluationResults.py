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

    self.refResult = EvalResults.EvaluationResult(self.refMeasurements, self.refInstanceMeasurements, 'TestEval',
                                                  'myWorkflow', 'myArtefacts', {'mod1': 'm1', 'mod2':'m2'},
                                                  self.refWeights, {'vn1':'a'}, {'vd1':'description'})
    self.refResultDefaults = EvalResults.EvaluationResult(self.refMeasurements, self.refInstanceMeasurements)

  def tearDown(self):
    try:
      shutil.rmtree(self.sessionDir)
    except:
      pass

  def assert_file_conten(self, filePathTest, filePathRef):
    with open(filePathRef) as refF:
      with open(filePathTest) as testF:
        ref = refF.read()
        test = testF.read()

        self.assertEqual(ref, test)

  def test_EvaluationResult_load(self):

    loadedResult = EvalResults.loadEvaluationResult(self.testResultFile)
    self.assert_(self.refResult, loadedResult)

  def test_EvaluationResult_save(self):
    testFilePath = os.path.join(self.sessionDir, 'result'+os.extsep+'eval')
    testFileDefaultPath = os.path.join(self.sessionDir, 'result_default'+os.extsep+'eval')

    EvalResults.saveEvaluationResult(testFilePath, self.refResult)
    self.assert_file_conten(testFilePath, self.testResultFile)

    EvalResults.saveEvaluationResult(testFileDefaultPath, self.refResultDefaults)
    self.assert_file_conten(testFileDefaultPath, self.testResultDefaultFile)


if __name__ == '__main__':
    unittest.main()