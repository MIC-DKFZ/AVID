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
from avid.actions.mitk.MitkMapImage import MitkMapImageBatchAction as map
from avid.common.artefact.defaultProps import TIMEPOINT
from avid.linkers import CaseLinker
from avid.selectors.keyValueSelector import ActionTagSelector

from avid.common.AVIDUrlLocater import getToolConfigPath

@unittest.skipIf(getToolConfigPath('MitkMapImage') is None, 'Tool MitkMapImage not installed on the system.')
class TestMitkMapImage(unittest.TestCase):


    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "mapRTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "mapRTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_MitkMapImage")
      self.testArtefactFile2 = os.path.join(os.path.split(__file__)[0],"data", "mapRTest", "testlist_2.avid")

      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

              
    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_MitkMapImage_action(self):
      
      action = map(ActionTagSelector("Moving"), ActionTagSelector("Registration"), ActionTagSelector("Target"), actionTag = "TestMapping")
      action.do()
                    
      self.assertEqual(action.isSuccess, True)

      action.do()
      self.assertEqual(action.isSkipped, True)


    def test_simple_MitkMapImage_action_alwaysdo(self):
      
      action = map(ActionTagSelector("Moving"), ActionTagSelector("Registration"), ActionTagSelector("Target"), alwaysDo = True, actionTag = "TestMapping_alwaysdo")
      action.do()
                    
      self.assertEqual(action.isSuccess, True)

      action.do()
      self.assertEqual(action.isSuccess, True)

    def test_MitkMapImage_action_caselinking(self):

        action = map(ActionTagSelector("Moving"), ActionTagSelector("Registration"), ActionTagSelector("Target"),
                      regLinker= CaseLinker(), actionTag = "TestMapping_caselinking")
        action.do()

        self.assertEqual(action.isSuccess, True)

        action.do()
        self.assertEqual(action.isSkipped, True)

    def test_MitkMapImage_action_inputIsReference(self):

        newsession = workflow.initSession(os.path.join(self.sessionDir, "testlist_2.avid"), expandPaths=True,
                                            bootstrapArtefacts=self.testArtefactFile2)

        action = map(ActionTagSelector("Moving"), ActionTagSelector("Registration"), ActionTagSelector("Target"),
                      alwaysDo=True, actionTag="TestMapping")
        action.do()
        self.assertEqual(action.isSuccess, True)
        self.assertEqual(action.outputArtefacts[0][TIMEPOINT], 1)

        action = map(ActionTagSelector("Moving"), ActionTagSelector("Registration"), ActionTagSelector("Target"),
                      inputIsArtefactReference=False, alwaysDo=True, actionTag="TestMapping")
        action.do()
        self.assertEqual(action.isSuccess, True)
        #now the template should be reference for output artefacts, thus the time point should be 0 (timpoint of
        #the template
        self.assertEqual(action.outputArtefacts[0][TIMEPOINT], 0)

    def test_MitkMapImage_action_supersampling(self):

        action = map(ActionTagSelector("Moving"), ActionTagSelector("Registration"), ActionTagSelector("Target"),
                     supersamplingFactor = 3, actionTag = "TestMapping_1ss")
        action.do()

        self.assertEqual(action.isSuccess, True)

    def test_MitkMapImage_action_supersampling3(self):

        action = map(ActionTagSelector("Moving"), ActionTagSelector("Registration"), ActionTagSelector("Target"),
                     supersamplingFactor = [3,2,1], actionTag = "TestMapping_3ss")
        action.do()

        self.assertEqual(action.isSuccess, True)


if __name__ == "__main__":
    unittest.main()