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
from avid.actions.rttb.DoseTool import DoseStatBatchAction as doseTool
from avid.common.AVIDUrlLocater import get_tool_config_file_path
from avid.selectors.keyValueSelector import ActionTagSelector


@unittest.skipIf(
    get_tool_config_file_path("DoseTool") is None,
    "Tool DoseTool not installed on the system.",
)
class TestDoseTool(unittest.TestCase):

    def setUp(self):
        self.testDataDir = os.path.join(
            os.path.split(__file__)[0], "data", "voxelizerTest"
        )
        self.testArtefactFile = os.path.join(
            os.path.split(__file__)[0], "data", "voxelizerTest", "testlist.avid"
        )
        self.testStructDef = os.path.join(
            os.path.split(__file__)[0], "data", "voxelizerTest", "structdef.xml"
        )
        self.sessionDir = os.path.join(
            os.path.split(__file__)[0], "temporary_test_DoseTool"
        )

        self.session = workflow.initSession(
            os.path.join(self.sessionDir, "test.avid"),
            expandPaths=True,
            bootstrapArtefacts=self.testArtefactFile,
            structDefinition=self.testStructDef,
        )

    def tearDown(self):
        try:
            shutil.rmtree(self.sessionDir)
        except:
            pass

    def test_simple_action(self):
        action = doseTool(
            ActionTagSelector("Reference"),
            ActionTagSelector("Struct"),
            ["Heart", "Breast"],
            actionTag="TestDoseTool",
        )
        action.do()

        self.assertEqual(action.isSuccess, True)
        self.assertEqual(len(action.outputArtefacts), 4)

        action.do()
        self.assertEqual(action.isSkipped, True)

    def test_simple_action_noDVH(self):
        action = doseTool(
            ActionTagSelector("Reference"),
            ActionTagSelector("Struct"),
            ["Heart", "Breast"],
            computeDVH=False,
            actionTag="TestDoseTool_noDVH",
        )
        action.do()

        self.assertEqual(action.isSuccess, True)
        self.assertEqual(len(action.outputArtefacts), 2)

    def test_simple_action_alwaysdo(self):
        action = doseTool(
            ActionTagSelector("Reference"),
            ActionTagSelector("Struct"),
            ["Heart"],
            actionTag="TestDoseTool_alwaysDo",
            alwaysDo=True,
        )
        action.do()

        self.assertEqual(action.isSuccess, True)

        action.do()
        self.assertEqual(action.isSuccess, True)


if __name__ == "__main__":
    unittest.main()
