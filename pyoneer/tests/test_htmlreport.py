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

from avid.common.osChecker import checkAndCreateDir
from pyoneer.evaluationResult import readEvaluationResult as readEvaluationResult, readOptimizationResult


def pyhtmlIsAvailable():
  try:
    import pyhtml
    return True
  except:
    return False


@unittest.skipIf(pyhtmlIsAvailable() is False, 'pyhtml is not installed on the system.')
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
    import pyoneer.htmlreport as htmlreport
    result = readEvaluationResult(self.testEvalResultFile)
    report = htmlreport.generateEvaluationReport(result)
    resultFile = os.path.join(self.sessionDir, "test.html")

    with open(resultFile, 'w') as fileHandle:
      fileHandle.write(report)

    self.assert_file_content(resultFile, self.testEvalHTMLRefFile)

  def test_generateOptimizationReport(self):
    import pyoneer.htmlreport as htmlreport
    result = readOptimizationResult(self.testOptResultFile)
    report = htmlreport.generateOptimizationReport(result)
    resultFile = os.path.join(self.sessionDir, "test.html")

    with open(resultFile, 'w') as fileHandle:
      fileHandle.write(report)

    self.assert_file_content(resultFile, self.testOptHTMLRefFile)

if __name__ == '__main__':
    unittest.main()