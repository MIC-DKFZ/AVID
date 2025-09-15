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

import unittest
import os
import shutil
import avid.common.workflow as workflow
from avid.actions.pointSetConversion import PointSetConversionBatchAction as psConversion
from avid.externals.fcsv import FORMAT_VALUE_SLICER_POINTSET
from avid.externals.matchPoint import FORMAT_VALUE_MATCHPOINT_POINTSET
from avid.selectors.keyValueSelector import ActionTagSelector
import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper

class TestPointSetConversion(unittest.TestCase):


    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "pointSetConversionTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "pointSetConversionTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_pointSetConversion")
      
      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

              
    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass


    def test_to_simpleMatchPoint(self):
      
      action = psConversion(ActionTagSelector("SourcePS"), targetformat=FORMAT_VALUE_MATCHPOINT_POINTSET,
                            actionTag="TestToMatchPoint", alwaysDo=False)
      action.do()
                    
      self.assertEqual(action.isSuccess, True)

      refFilePath = os.path.join(self.testDataDir, "refMatchPoint"+os.extsep+"txt")
      resultFilePath = artefactHelper.getArtefactProperty(action._actions[0].outputArtefacts[0],
                                                      artefactProps.URL)
      with open(refFilePath) as refFile:
          with open(resultFilePath) as resultFile:
              self.assertEqual(refFile.read(), resultFile.read())

      resultFilePath = artefactHelper.getArtefactProperty(action._actions[1].outputArtefacts[0],
                                                      artefactProps.URL)
      with open(refFilePath) as refFile:
          with open(resultFilePath) as resultFile:
              self.assertEqual(refFile.read(), resultFile.read())

      action.do()
      self.assertEqual(action.isSkipped, True)

    def test_to_fcsv(self):
        action = psConversion(ActionTagSelector("SourcePS"), targetformat=FORMAT_VALUE_SLICER_POINTSET,
                              actionTag="TestToFCSV", alwaysDo=False)
        action.do()

        self.assertEqual(action.isSuccess, True)

        refFilePath = os.path.join(self.testDataDir, "refMatchPoint" + os.extsep + "fcsv")
        resultFilePath = artefactHelper.getArtefactProperty(action._actions[0].outputArtefacts[0],
                                                        artefactProps.URL)
        with open(refFilePath) as refFile:
            with open(resultFilePath) as resultFile:
                self.assertEqual(refFile.read(), resultFile.read())

        refFilePath = os.path.join(self.testDataDir, "ref3dslicer" + os.extsep + "fcsv")
        resultFilePath = artefactHelper.getArtefactProperty(action._actions[1].outputArtefacts[0],
                                                        artefactProps.URL)
        with open(refFilePath) as refFile:
            with open(resultFilePath) as resultFile:
                self.assertEqual(refFile.read(), resultFile.read())

        action.do()
        self.assertEqual(action.isSkipped, True)

if __name__ == "__main__":
    unittest.main()