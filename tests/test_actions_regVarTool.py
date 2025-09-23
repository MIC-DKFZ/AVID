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
from avid.actions.regVarTool import RegVarToolBatchAction as regVarTool
from avid.common import AVIDUrlLocater
from avid.common.AVIDUrlLocater import get_tool_config_file_path
from avid.selectors import FormatSelector
from avid.selectors.keyValueSelector import ActionTagSelector


@unittest.skipIf(
    get_tool_config_file_path("RegVarTool") is None,
    "Tool RegVarTool not installed on the system.",
)
class TestRegVarTool(unittest.TestCase):

    def setUp(self):
        self.testDataDir = os.path.join(
            os.path.split(__file__)[0], "data", "regVarToolTest"
        )
        self.testArtefactFile = os.path.join(
            os.path.split(__file__)[0], "data", "mapRTest", "testlist.avid"
        )
        self.sessionDir = os.path.join(
            os.path.split(__file__)[0], "temporary_test_regVarTool"
        )
        self.session = workflow.initSession(
            os.path.join(self.sessionDir, "test.avid"),
            expandPaths=True,
            bootstrapArtefacts=self.testArtefactFile,
        )

        self.numberOfVariations = 3
        self.dllPath = AVIDUrlLocater.get_tool_config_dir("RegVarTool")
        self.algorithmDLLEuler = str(
            self.dllPath / "mdra-0-12_RegVariationRandomGaussianEuler.dll"
        )
        self.algorithmDLLTPS = str(
            self.dllPath / "mdra-0-12_RegVariationKernelRandomGaussianTPS.dll"
        )
        self.parameters = {
            "MeanGlobal": "0.0",
            "StandardDeviationGlobal": "1.0",
            "Seed": "0",
        }

    def tearDown(self):
        try:
            shutil.rmtree(self.sessionDir)
        except:
            pass

    def test_simple_regvartool_action(self):
        action = regVarTool(
            ActionTagSelector("Registration") + FormatSelector("MatchPoint"),
            self.numberOfVariations,
            algorithmDLL=self.algorithmDLLEuler,
            actionTag="TestRegVar",
        )
        action.do()

        self.assertEqual(action.isSuccess, True)

        action.do()
        self.assertEqual(action.isSkipped, True)

    def test_simple_regvar_action_alwaysdo(self):

        action = regVarTool(
            ActionTagSelector("Registration") + FormatSelector("MatchPoint"),
            self.numberOfVariations,
            algorithmDLL=self.algorithmDLLEuler,
            alwaysDo=True,
            actionTag="TestRegVar",
        )
        action.do()

        self.assertEqual(action.isSuccess, True)

        action.do()
        self.assertEqual(action.isSuccess, True)

    def test_simple_regvar_action_parameters(self):
        action = regVarTool(
            ActionTagSelector("Registration") + FormatSelector("MatchPoint"),
            self.numberOfVariations,
            algorithmDLL=self.algorithmDLLEuler,
            regParameters=self.parameters,
            actionTag="TestRegVarParam",
        )
        action.do()

        self.assertEqual(action.isSuccess, True)

    def test_simple_regvar_action_image(self):
        action = regVarTool(
            ActionTagSelector("Registration") + FormatSelector("MatchPoint"),
            self.numberOfVariations,
            algorithmDLL=self.algorithmDLLTPS,
            templateSelector=ActionTagSelector("Target"),
            actionTag="TestRegVarImage",
        )
        action.do()

        self.assertEqual(action.isSuccess, True)


if __name__ == "__main__":
    unittest.main()
