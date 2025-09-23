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
from avid.actions.rttb.bioModelCalc import \
    BioModelCalcBatchAction as bioModelCalc
from avid.common.AVIDUrlLocater import get_tool_config_file_path
from avid.selectors.keyValueSelector import ActionTagSelector


@unittest.skipIf(get_tool_config_file_path('BioModelCalc') is None, 'Tool BioModelCalc not installed on the system.')
class TestBioModelCalc(unittest.TestCase):
  def setUp(self):
    self.testDataDir = os.path.join(os.path.split(__file__)[0], "data", "bioModelCalcTest")
    self.testArtefactFile = os.path.join(os.path.split(__file__)[0], "data", "bioModelCalcTest", "testlist.avid")
    self.sessionDir = os.path.join(os.path.split(__file__)[0], "temporary_test_bioModelCalc")

    self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True,
                                        bootstrapArtefacts=self.testArtefactFile)

  def tearDown(self):
    try:
      shutil.rmtree(self.sessionDir)
    except:
      pass

  def test_simple_bio_model_calc_action(self):

    action = bioModelCalc(ActionTagSelector("Dose"), modelParameters=[0.1, 0.01], actionTag="SimpleBioModelCalc")
    action.do()
    self.assertEqual(action.isSuccess, True)
    action.do()
    self.assertEqual(action.isSkipped, True)


if __name__ == "__main__":
  unittest.main()
