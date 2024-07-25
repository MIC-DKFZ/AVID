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
import shutil
import unittest
import avid.common.workflow as workflow
import os
from avid.actions.dummy import DummyBatchAction

import avid.common.artefact.generator as artefactGenerator
import avid.common.artefact as artefact
import avid.common.artefact.defaultProps as artefactProps
from avid.selectors import SelectorBase


class TestSelector(SelectorBase):
  '''
      Special selector that will only select the artefacts that are passed with init in order to directly control
      what the action will get.
  '''

  def __init__(self, legalArtefacts):
    ''' init '''
    super().__init__()
    self._legalArtefacts = legalArtefacts

  def getSelection(self, workflowData):
    '''Filters the given list of entries and returns all selected entries'''
    result = []
    for a in workflowData:
        if a in self._legalArtefacts:
            result.append(a)
    return self._legalArtefacts


class Test(unittest.TestCase):

    def setUp(self):
        self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_actions")
        self.testDataDir = os.path.join(os.path.split(__file__)[0],"data")

        self.a_valid = artefactGenerator.generateArtefactEntry("Case1", 0, 0, "Action1", artefactProps.TYPE_VALUE_RESULT, "dummy", os.path.join(self.testDataDir, "artefact1.txt"))
        self.a_valid2 = artefactGenerator.generateArtefactEntry("Case2", 2, 0, "Action3", artefactProps.TYPE_VALUE_RESULT, "dummy", os.path.join(self.testDataDir, "artefact2.txt"))
        self.a_NoneURL = artefactGenerator.generateArtefactEntry("Case2", 1, 0, "Action1", artefactProps.TYPE_VALUE_RESULT, "dummy", None)
        self.a_NoFile = artefactGenerator.generateArtefactEntry("Case3", 1, 0, "Action1", artefactProps.TYPE_VALUE_RESULT, "dummy", "notexistingFile")
        self.a_Invalid = artefactGenerator.generateArtefactEntry("Case2", 2, 0, "Action1", artefactProps.TYPE_VALUE_RESULT, "dummy", os.path.join(self.testDataDir, "artefact2.txt"), None, True)
        
        self.a_valid_new = artefactGenerator.generateArtefactEntry("Case1", 0, 0, "Action1", artefactProps.TYPE_VALUE_RESULT, "dummy", os.path.join(self.testDataDir, "artefact1.txt"))
        self.a_valid2_new = artefactGenerator.generateArtefactEntry("Case2", 2, 0, "Action3", artefactProps.TYPE_VALUE_RESULT, "dummy", os.path.join(self.testDataDir, "artefact2.txt"))
        self.a_Invalid_new = artefactGenerator.generateArtefactEntry("Case2", 2, 0, "Action1", artefactProps.TYPE_VALUE_RESULT, "dummy", os.path.join(self.testDataDir, "artefact2.txt"))
 
        self.session = workflow.Session("session1", self.sessionDir)
        artefact.addArtefactToWorkflowData(self.session.artefacts,self.a_valid)
        artefact.addArtefactToWorkflowData(self.session.artefacts,self.a_valid2)
        artefact.addArtefactToWorkflowData(self.session.artefacts,self.a_NoneURL)
        artefact.addArtefactToWorkflowData(self.session.artefacts,self.a_NoFile)
        artefact.addArtefactToWorkflowData(self.session.artefacts,self.a_Invalid)
        

    def tearDown(self):
        try:
            shutil.rmtree(self.sessionDir)
        except:
            pass

    def test_simelar_exisiting_alwaysDo(self):
      workflow.currentGeneratedSession = self.session
      action = DummyBatchAction(TestSelector([self.a_valid_new, self.a_valid2_new]),"Action1", alwaysDo = True)
      
      action.do()
      
      self.assertTrue(action.isSuccess)
      self.assertIn(self.a_valid_new, action.outputArtefacts)
      self.assertIn(self.a_valid2_new, action.outputArtefacts)
      self.assertEqual(len(action.outputArtefacts), 2)
      self.assertIn(action._actions[0], self.session.executed_actions)
      self.assertIn(action._actions[1], self.session.executed_actions)
      self.assertIn(self.a_valid_new, self.session.artefacts)
      self.assertIn(self.a_valid2_new, self.session.artefacts)
      

    def test_simelar_exisiting_alwaysOff(self):
      workflow.currentGeneratedSession = self.session
      action = DummyBatchAction(TestSelector([self.a_valid_new, self.a_valid2_new]),"Action1", alwaysDo = False)
      
      action.do()
      
      self.assertTrue(action.isSkipped)
      self.assertIn(self.a_valid, action.outputArtefacts)
      self.assertIn(self.a_valid2, action.outputArtefacts)
      self.assertEqual(len(action.outputArtefacts), 2)
      self.assertIn(action._actions[0], self.session.executed_actions)
      self.assertIn(action._actions[1], self.session.executed_actions)
      self.assertIn(self.a_valid, self.session.artefacts)
      self.assertIn(self.a_valid2, self.session.artefacts)
      self.assertFalse(self.a_valid_new in self.session.artefacts)
      self.assertFalse(self.a_valid2_new in self.session.artefacts)


    def test_simelar_mixed_alwaysDo(self):
      workflow.currentGeneratedSession = self.session
      action = DummyBatchAction(TestSelector([self.a_valid_new, self.a_Invalid_new]),"Action1", alwaysDo = True)
      
      action.do()
      
      self.assertTrue(action.isSuccess)
      self.assertIn(self.a_valid_new, action.outputArtefacts)
      self.assertIn(self.a_Invalid_new, action.outputArtefacts)
      self.assertEqual(len(action.outputArtefacts), 2)
      self.assertIn(action._actions[0], self.session.executed_actions)
      self.assertIn(action._actions[1], self.session.executed_actions)
      self.assertIn(self.a_valid_new, self.session.artefacts)
      self.assertIn(self.a_Invalid_new, self.session.artefacts)


    def test_simelar_mixed_alwaysOff(self):
      workflow.currentGeneratedSession = self.session
      action = DummyBatchAction(TestSelector([self.a_valid_new, self.a_Invalid_new]),"Action1", alwaysDo = False)
      
      action.do()
      
      self.assertTrue(action.isSuccess)
      self.assertIn(self.a_valid, action.outputArtefacts)
      self.assertIn(self.a_Invalid_new, action.outputArtefacts)
      self.assertEqual(len(action.outputArtefacts), 2)
      self.assertIn(action._actions[0], self.session.executed_actions)
      self.assertIn(action._actions[1], self.session.executed_actions)
      self.assertIn(self.a_valid, self.session.artefacts)
      self.assertIn(self.a_Invalid_new, self.session.artefacts)
      self.assertFalse(self.a_valid_new in self.session.artefacts)
      self.assertFalse(self.a_Invalid in self.session.artefacts)


    def test_failure_mixed_alwaysOn(self):
      workflow.currentGeneratedSession = self.session
      action = DummyBatchAction(TestSelector([self.a_valid_new, self.a_NoFile]),"Action1", alwaysDo = True)
      
      action.do()
      
      self.assertTrue(action.isFailure)
      self.assertIn(self.a_valid_new, action.outputArtefacts)
      self.assertIn(self.a_NoFile, action.outputArtefacts)
      self.assertEqual(len(action.outputArtefacts), 2)
      self.assertIn(action._actions[0], self.session.executed_actions)
      self.assertIn(action._actions[1], self.session.executed_actions)
      self.assertIn(self.a_valid_new, self.session.artefacts)
      self.assertIn(self.a_NoFile, self.session.artefacts)
      self.assertTrue(action.outputArtefacts[1][artefactProps.INVALID])

    
    def test_failure_mixed_alwaysOff(self):
      workflow.currentGeneratedSession = self.session
      action = DummyBatchAction(TestSelector([self.a_valid_new, self.a_NoFile]),"Action1")
      
      action.do()
      
      self.assertTrue(action.isFailure)
      self.assertIn(self.a_valid, action.outputArtefacts)
      self.assertIn(self.a_NoFile, action.outputArtefacts)
      self.assertEqual(len(action.outputArtefacts), 2)
      self.assertIn(action._actions[0], self.session.executed_actions)
      self.assertIn(action._actions[1], self.session.executed_actions)
      self.assertIn(self.a_valid, self.session.artefacts)
      self.assertIn(self.a_NoFile, self.session.artefacts)
      self.assertTrue(action.outputArtefacts[1][artefactProps.INVALID])


if __name__ == "__main__":
    unittest.main()