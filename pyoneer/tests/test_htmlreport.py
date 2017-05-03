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
from pyoneer.evaluationResult import readEvaluationResult as readEvaluationResult, readOptimizationResult


class TestHTMLreport(unittest.TestCase):
  def setUp(self):

    self.testDataDir = os.path.join(os.path.split(__file__)[0],"data")
    self.testResultFile = os.path.join(os.path.split(__file__)[0],"data",'evaluationResults', "result"+os.extsep+"eval")
    self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary", "test_evaluationResults")

    self.testOptResultFile = os.path.join(os.path.split(__file__)[0],"data",'evaluationResults', "result"+os.extsep+"opt")

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
    result = readEvaluationResult(self.testResultFile)
    report = htmlreport.generateEvaluationReport(result)

    with open(os.path.join(self.testDataDir, "test.html"), 'w') as fileHandle:
      fileHandle.write(report)

    self.assertEqual(report, '')

  def test_generateOptimizationReport(self):
    result = readOptimizationResult(self.testOptResultFile)
    report = htmlreport.generateOptimizationReport(result)

    with open(os.path.join(self.testDataDir, "test.html"), 'w') as fileHandle:
      fileHandle.write(report)

    self.assertEqual(report, '')

if __name__ == '__main__':
    unittest.main()