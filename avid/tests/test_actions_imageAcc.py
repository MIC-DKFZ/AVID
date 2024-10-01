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
from avid.actions.rttb.imageAcc import ImageAccBatchAction as imageAcc
from avid.selectors.keyValueSelector import ActionTagSelector
from avid.common.AVIDUrlLocater import getToolConfigPath

@unittest.skipIf(getToolConfigPath('DoseAcc') is None, 'Tool DoseAcc not installed on the system.')
class TestDoseAcc(unittest.TestCase):


    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "imageAccTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "imageAccTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_imageAcc")
      
      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

              
    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_image_acc_action(self):
      
      action = imageAcc(ActionTagSelector("Image"), actionTag = "SimpleAcc")
      action.do()
      self.assertEqual(action.isSuccess, True)
      action.do()
      self.assertEqual(action.isSkipped, True)
  
      action = imageAcc(ActionTagSelector("Image"), ActionTagSelector("Registration"), actionTag = "Acc+Reg")
      action.do()
      self.assertEqual(action.isSuccess, True)
      action.do()
      self.assertEqual(action.isSkipped, True)

    def test_simple_image_acc_action_alwaysdo(self):
      
      action = imageAcc(ActionTagSelector("Image"), actionTag = "SimpleAcc", alwaysDo = True)
      action.do()
      self.assertEqual(action.isSuccess, True)
      action.do()
      self.assertEqual(action.isSuccess, True)


if __name__ == "__main__":
    unittest.main()