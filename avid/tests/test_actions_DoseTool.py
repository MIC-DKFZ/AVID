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
from avid.actions.DoseTool import DoseStatBatchAction as doseTool
from avid.selectors.keyValueSelector import ActionTagSelector
from avid.common.AVIDUrlLocater import getToolConfigPath


@unittest.skipIf(getToolConfigPath('DoseTool') is None, 'Tool DoseTool not installed on the system.')
class TestDoseTool(unittest.TestCase):

    def setUp(self):
        self.testDataDir = os.path.join(os.path.split(__file__)[0], "data", "voxelizerTest")
        self.testArtefactFile = os.path.join(os.path.split(__file__)[0], "data", "voxelizerTest", "testlist.avid")
        self.testStructDef = os.path.join(os.path.split(__file__)[0], "data", "voxelizerTest", "structdef.xml")
        self.sessionDir = os.path.join(os.path.split(__file__)[0], "temporary_test_DoseTool")

        self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"),
                                            expandPaths=True, bootstrapArtefacts=self.testArtefactFile,
                                            structDefinition=self.testStructDef)

    def tearDown(self):
        try:
            shutil.rmtree(self.sessionDir)
        except:
            pass

    def test_simple_action(self):
        action = doseTool(ActionTagSelector('Reference'), ActionTagSelector('Struct'),
                          ['Heart', 'Breast'], actionTag="TestDoseTool")
        token = action.do()

        self.assertEqual(token.isSuccess(), True)
        self.assertEqual(len(action.outputArtefacts), 4)

        token = action.do()
        self.assertEqual(token.isSkipped(), True)

    def test_simple_action_noDVH(self):
        action = doseTool(ActionTagSelector('Reference'), ActionTagSelector('Struct'),
                          ['Heart', 'Breast'], computeDVH=False, actionTag="TestDoseTool_noDVH")
        token = action.do()

        self.assertEqual(token.isSuccess(), True)
        self.assertEqual(len(action.outputArtefacts), 2)

    def test_simple_action_alwaysdo(self):
        action = doseTool(ActionTagSelector('Reference'), ActionTagSelector('Struct'),
                          ['Heart'], actionTag="TestDoseTool_alwaysDo", alwaysDo=True)
        token = action.do()

        self.assertEqual(token.isSuccess(), True)

        token = action.do()
        self.assertEqual(token.isSuccess(), True)


if __name__ == "__main__":
    unittest.main()
