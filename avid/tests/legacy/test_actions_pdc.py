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
from avid.actions.pdc import pdcBatchAction as pdc
from avid.selectors.keyValueSelector import ActionTagSelector
from avid.common.artefact import generateArtefactEntry
import avid.common.artefact.defaultProps as defaultProps
from avid.common.AVIDUrlLocater import getToolConfigPath

@unittest.skipIf(getToolConfigPath('pdc++') is None, 'Tool pdc++ not installed on the system.')
class TestPDC(unittest.TestCase):


    def setUp(self):
      
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "pdcTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "pdcTest", "testlist.avid")
            
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_pdc")

      self.batPath = os.path.join(os.path.split(__file__)[0],"data", "pdcTest", "PDC_template.bat")
         
      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True)
      
      pdcDataPath = os.path.join(os.path.dirname(getToolConfigPath('pdc++')),'Resources', 'TestData','data','2000_TEST_B')
      plan = generateArtefactEntry('case1', None, 0, 'Plan', defaultProps.TYPE_VALUE_RESULT, defaultProps.FORMAT_VALUE_VIRTUOS, os.path.join(pdcDataPath, '2000_TEST_B108.pln'))
      self.session.artefacts.append(plan)
      ct = generateArtefactEntry('case1', None, 0, 'BPLCT', defaultProps.TYPE_VALUE_RESULT, defaultProps.FORMAT_VALUE_VIRTUOS, os.path.join(pdcDataPath, '2000_TEST_B000.ctx.gz'))
      self.session.artefacts.append(ct)
      structurset = generateArtefactEntry('case1', None, 0, 'Struct', defaultProps.TYPE_VALUE_RESULT, defaultProps.FORMAT_VALUE_VIRTUOS, os.path.join(pdcDataPath, '2000_TEST_B000.vdx'))
      self.session.artefacts.append(structurset)

              
    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_pdc_action(self):
      
      action = pdc(ActionTagSelector("BPLCT"), ActionTagSelector("Plan"), ActionTagSelector("Struct"), actionTag = "TestPDC", executionBat = self.batPath)     
      token = action.do()
      self.assertEqual(token.isSuccess(), True)


if __name__ == "__main__":
    unittest.main()