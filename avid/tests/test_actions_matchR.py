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
from avid.actions.matchR import matchRBatchAction as matchR
from avid.common.AVIDUrlLocater import getToolsPath
from avid.selectors.keyValueSelector import ActionTagSelector
from avid.common.AVIDUrlLocater import getToolConfigPath

@unittest.skipIf(getToolConfigPath('matchR') is None, 'Tool matchR not installed on the system.')
class TestMatchR(unittest.TestCase):


    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "matchRTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "matchRTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_matchR")

      self.dllPath = os.path.join(getToolsPath(), "matchR")
      self.itkAlgorithm = os.path.join(self.dllPath, "mdra-0-13_ITKEuler3DMattesMIMultiRes.dll")
      
      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

              
    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_reg_action(self):
      
      action = matchR(ActionTagSelector("Target"), ActionTagSelector("Moving"), algorithm = self.itkAlgorithm, actionTag = "TestReg")
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSkipped(), True)


    def test_simple_reg_action_always_do(self):
      
      action = matchR(ActionTagSelector("Target"), ActionTagSelector("Moving"), algorithm = self.itkAlgorithm, actionTag = "TestReg", alwaysDo = True)
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSuccess(), True)


if __name__ == "__main__":
    unittest.main()