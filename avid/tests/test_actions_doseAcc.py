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
from avid.actions.doseAcc import DoseAccBatchAction as doseAcc
from avid.selectors.keyValueSelector import ActionTagSelector
from avid.sorter import BaseSorter

from avid.common.AVIDUrlLocater import getToolConfigPath

@unittest.skipIf(getToolConfigPath('DoseAcc') is None, 'Tool DoseAcc not installed on the system.')
class TestDoseAcc(unittest.TestCase):


    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "doseAccTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "doseAccTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_doseAcc")
      
      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

              
    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_dose_acc_action(self):
      
      action = doseAcc(ActionTagSelector("Dose"), actionTag = "SimpleAcc")      
      token = action.do()
      self.assertEqual(token.isSuccess(), True)
      token = action.do()
      self.assertEqual(token.isSkipped(), True)
  
      action = doseAcc(ActionTagSelector("Dose"), ActionTagSelector("Registration"), actionTag = "Acc+Reg")     
      token = action.do()
      self.assertEqual(token.isSuccess(), True)
      token = action.do()
      self.assertEqual(token.isSkipped(), True)

      action = doseAcc(ActionTagSelector("Dose"), ActionTagSelector("Registration"), actionTag = "Acc+Reg+noSort", doseSorter = BaseSorter())      
      token = action.do()
      self.assertEqual(token.isSuccess(), True)
      token = action.do()
      self.assertEqual(token.isSkipped(), True)

      action = doseAcc(ActionTagSelector("Dose"), ActionTagSelector("Registration"), ActionTagSelector("Plan"), actionTag = "Acc+Reg+Plan")    
      token = action.do()
      self.assertEqual(token.isSuccess(), True)
      token = action.do()
      self.assertEqual(token.isSkipped(), True)

      action = doseAcc(ActionTagSelector("Dose"), ActionTagSelector("Registration"), ActionTagSelector("Plan"), interpolator="rosu", actionTag = "Acc+Reg+Plan+Interpolation")
      token = action.do()
      self.assertEqual(token.isSuccess(), True)
      token = action.do()
      self.assertEqual(token.isSkipped(), True)


    def test_simple_dose_acc_action_alwaysdo(self):
      
      action = doseAcc(ActionTagSelector("Dose"), actionTag = "SimpleAcc", alwaysDo = True)      
      token = action.do()
      self.assertEqual(token.isSuccess(), True)
      token = action.do()
      self.assertEqual(token.isSuccess(), True)


if __name__ == "__main__":
    unittest.main()