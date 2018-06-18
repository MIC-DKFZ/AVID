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

import pyoneer.htmlreport as htmlreport
from avid.common.osChecker import checkAndCreateDir
from pyoneer.evaluationResult import readEvaluationResult as readEvaluationResult, readOptimizationResult


class TestHTMLreport(unittest.TestCase):
  def setUp(self):

    self.testDataDir = os.path.join(os.path.split(__file__)[0],"data")
    self.testEvalResultFile = os.path.join(os.path.split(__file__)[0],"data",'evaluationResults', "result"+os.extsep+"eval")
    self.testOptResultFile = os.path.join(os.path.split(__file__)[0],"data",'evaluationResults', "result"+os.extsep+"opt")
    self.testEvalHTMLRefFile = os.path.join(os.path.split(__file__)[0],"data",'htmlReport', "eval"+os.extsep+"html")
    self.testOptHTMLRefFile = os.path.join(os.path.split(__file__)[0],"data",'htmlReport', "opt"+os.extsep+"html")

    self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary", "test_evaluationResults")
    checkAndCreateDir(self.sessionDir)

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

  def test_generateEvaluationReport(self):
    result = readEvaluationResult(self.testEvalResultFile)
    report = htmlreport.generateEvaluationReport(result)
    resultFile = os.path.join(self.sessionDir, "test.html")

    with open(resultFile, 'w') as fileHandle:
      fileHandle.write(report)

    self.assert_file_content(resultFile, self.testEvalHTMLRefFile)

  def test_generateOptimizationReport(self):
    result = readOptimizationResult(self.testOptResultFile)
    report = htmlreport.generateOptimizationReport(result)
    resultFile = os.path.join(self.sessionDir, "test.html")

    with open(resultFile, 'w') as fileHandle:
      fileHandle.write(report)

    self.assert_file_content(resultFile, self.testOptHTMLRefFile)

if __name__ == '__main__':
    unittest.main()