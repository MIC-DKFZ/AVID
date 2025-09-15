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
import avid.common.artefact.generator as artefactGenerator
from avid.actions.dummy import DummySingleAction as DummyAction
import avid.common.workflow as workflow
from avid.actions.threadingScheduler import ThreadingScheduler 

class TestThreadingScheduler(unittest.TestCase):
  def setUp(self):
    self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_actions")
    self.testDataDir = os.path.join(os.path.split(__file__)[0],"data")
       
    self.session = workflow.Session("session1", self.sessionDir)
            
    self.a1 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action1", "result", "dummy", os.path.join(self.testDataDir, "artefact1.txt"))
    self.a2 = artefactGenerator.generateArtefactEntry("Case1", None, 1, "Action2", "result", "dummy", os.path.join(self.testDataDir, "artefact1.txt"))
    self.a3 = artefactGenerator.generateArtefactEntry("Case1", None, 2, "Action3", "result", "dummy", os.path.join(self.testDataDir, "artefact1.txt"))
    self.a4 = artefactGenerator.generateArtefactEntry("Case2", None, 3, "Action4", "result", "dummy", os.path.join(self.testDataDir, "artefact1.txt"))
    self.a5 = artefactGenerator.generateArtefactEntry("Case2", None, 4, "Action5", "result", "dummy", os.path.join(self.testDataDir, "artefact1.txt"))
    self.a6 = artefactGenerator.generateArtefactEntry("Case2", None, 5, "Action6", "result", "dummy", os.path.join(self.testDataDir, "artefact1.txt"))

    self.session = workflow.Session("session1", self.sessionDir)
    workflow.currentGeneratedSession =self.session
    
    self.action1 = DummyAction([self.a1],"Action1", True)                
    self.action2 = DummyAction([self.a2],"Action2", True)                
    self.action3 = DummyAction([self.a3],"Action3", True)                
    self.action4 = DummyAction([self.a4],"Action4", True)                
    self.action5 = DummyAction([self.a5],"Action5", True)                
    self.action6 = DummyAction([self.a6],"Action6", True)
    
    self.actionList = [self.action1, self.action2, self.action3, self.action4, self.action5, self.action6]                


  def test_Scheduler(self):
    
    scheduler = ThreadingScheduler(3)
    
    scheduler.execute(self.actionList)
    
    self.assertIn(self.a1, self.session.artefacts)
    self.assertIn(self.a2, self.session.artefacts)
    self.assertIn(self.a3, self.session.artefacts)
    self.assertIn(self.a4, self.session.artefacts)
    self.assertIn(self.a5, self.session.artefacts)
    self.assertIn(self.a6, self.session.artefacts)
    
    self.assertEqual(len(self.session.executed_actions), 6)
    self.assertFalse(self.session.hasFailedActions())

if __name__ == '__main__':
    unittest.main()