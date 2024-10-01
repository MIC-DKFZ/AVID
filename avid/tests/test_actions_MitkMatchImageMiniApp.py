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

import avid.common.workflow as workflow
from avid.actions.mitk.MitkMatchImage import MitkMatchImageBatchAction as mitkMatch
from avid.common.AVIDUrlLocater import getToolsPath
from avid.selectors.keyValueSelector import ActionTagSelector
from avid.common.AVIDUrlLocater import getToolConfigPath

@unittest.skipIf(getToolConfigPath('MitkMatchImage') is None, 'Tool MitkMatchImage not installed on the system.')
class TestMatchR(unittest.TestCase):


    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "matchRTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "matchRTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_matchR")

      self.dllPath = os.path.join(getToolsPath(), "MitkMatchImage")
      self.itkAlgorithm = "mdra-0-14_MITK_MultiModal_rigid_default.dll"

      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

              
    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_reg_action(self):
      
      action = mitkMatch(ActionTagSelector("Target"), ActionTagSelector("Moving"), algorithm = self.itkAlgorithm, actionTag = "TestReg")
      action.do()
                    
      self.assertEqual(action.isSuccess, True)

      action.do()
      self.assertEqual(action.isSkipped, True)


    def test_simple_reg_action_always_do(self):
      
      action = mitkMatch(ActionTagSelector("Target"), ActionTagSelector("Moving"), algorithm = self.itkAlgorithm, actionTag = "TestReg", alwaysDo = True)
      action.do()
                    
      self.assertEqual(action.isSuccess, True)

      action.do()
      self.assertEqual(action.isSuccess, True)


if __name__ == "__main__":
    unittest.main()