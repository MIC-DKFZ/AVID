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
from avid.actions.plastimatch.plmRTSSMap import PlmRTSSMapBatchAction as plmRTTSMap
from avid.common.artefact.defaultProps import FORMAT_VALUE_DCM
from avid.externals.plastimatch import FORMAT_VALUE_PLM_CXT
from avid.selectors.keyValueSelector import ActionTagSelector
from avid.common.AVIDUrlLocater import get_tool_config_file_path

@unittest.skipIf(get_tool_config_file_path('plastimatch') is None, 'Tool Plastimatch not installed on the system.')
class TestPlmRTSSMap(unittest.TestCase):

    def setUp(self):
      self.testRTSS = os.path.join(os.path.split(__file__)[0],"data", "voxelizerTest", "rtss.dcm")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_plmRTSSMap")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "voxelizerTest", "testlist.avid")

      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"),
                                          expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_action(self):
      
      action = plmRTTSMap(ActionTagSelector('Struct'), outputFormat = FORMAT_VALUE_DCM,
                          actionTag = "TestPlmRTSSMap")
      action.do()
                    
      self.assertEqual(action.isSuccess, True)

      action.do()
      self.assertEqual(action.isSkipped, True)


    def test_action_cxt(self):
        action = plmRTTSMap(ActionTagSelector('Struct'), outputFormat=FORMAT_VALUE_PLM_CXT,
                            actionTag="TestPlmRTSSMap")
        action.do()

        self.assertEqual(action.isSuccess, True)

    #TODO ad test that checks mapping with reg
    #def test_action_with_reg(self):

if __name__ == "__main__":
    unittest.main()