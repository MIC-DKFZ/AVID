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
from avid.actions.vioConvert import VioConvertBatchAction as vioConvert
from avid.selectors.keyValueSelector import ActionTagSelector
from avid.common.AVIDUrlLocater import getToolConfigPath


@unittest.skipIf(getToolConfigPath('vioConvert') is None, 'Tool vioConvert not installed on the system.')
class TestVioConvert(unittest.TestCase):

    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0], "data", "vioConvertTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0], "data", "vioConvertTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0], "temporary", "test_vioConvert")
      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_conversion_action(self):
        action = vioConvert(ActionTagSelector("Input"), actionTag="TestConvert")
        token = action.do()

        self.assertEqual(token.isSuccess(), True)

        token = action.do()
        self.assertEqual(token.isSkipped(), True)

    def test_simple_conversion_action_always_do(self):
        action = vioConvert(ActionTagSelector("Input"), actionTag="TestConvert", alwaysDo=True)
        token = action.do()

        self.assertEqual(token.isSuccess(), True)
        token = action.do()
        self.assertEqual(token.isSuccess(), True)

if __name__ == "__main__":
    unittest.main()
