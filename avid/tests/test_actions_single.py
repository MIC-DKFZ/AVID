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
from avid.actions.dummy import DummySingleAction
import avid.common.artefact.generator as artefactGenerator
import avid.common.artefact as artefact
import avid.common.artefact.defaultProps as artefactProps
from avid.common.artefact import Artefact

class Test(unittest.TestCase):

    def setUp(self):
        self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_actions")
        self.testDataDir = os.path.join(os.path.split(__file__)[0],"data")

        self.a_valid = artefactGenerator.generateArtefactEntry("Case1", 0, 0, "Action1", artefactProps.TYPE_VALUE_RESULT, "dummy", os.path.join(self.testDataDir, "artefact1.txt"))
        self.a_NoneURL = artefactGenerator.generateArtefactEntry("Case2", 1, 0, "Action1", artefactProps.TYPE_VALUE_RESULT, "dummy", None)
        self.a_NoFile = artefactGenerator.generateArtefactEntry("Case3", 1, 0, "Action1", artefactProps.TYPE_VALUE_RESULT, "dummy", "notexistingFile", None, True)
        self.a_Invalid = artefactGenerator.generateArtefactEntry("Case2", 2, 0, "Action1", artefactProps.TYPE_VALUE_RESULT, "dummy", os.path.join(self.testDataDir, "artefact2.txt"), None, True)
        
        self.a_valid_new = artefactGenerator.generateArtefactEntry("Case1", 0, 0, "Action1", artefactProps.TYPE_VALUE_RESULT, "dummy", os.path.join(self.testDataDir, "artefact1.txt"))
        self.a_NoneURL_new = artefactGenerator.generateArtefactEntry("Case2", 1, 0, "Action1", artefactProps.TYPE_VALUE_RESULT, "dummy", os.path.join(self.testDataDir, "artefact2.txt"))
        self.a_NoFile_new = artefactGenerator.generateArtefactEntry("Case3", 1, 0, "Action1", artefactProps.TYPE_VALUE_RESULT, "dummy", os.path.join(self.testDataDir, "artefact2.txt"))
        self.a_Invalid_new = artefactGenerator.generateArtefactEntry("Case2", 2, 0, "Action1", artefactProps.TYPE_VALUE_RESULT, "dummy", os.path.join(self.testDataDir, "artefact2.txt"))
        self.a_valid2_new = artefactGenerator.generateArtefactEntry("Case4", 2, 0, "Action2", artefactProps.TYPE_VALUE_RESULT, "dummy", os.path.join(self.testDataDir, "artefact2.txt"))
 
        self.a_NoFile2 = artefactGenerator.generateArtefactEntry("Case6", 0, 0, "Action1", artefactProps.TYPE_VALUE_RESULT, "dummy", os.path.join(self.testDataDir, "notExstingFile.txt"))
        self.a_NoResult = artefactGenerator.generateArtefactEntry("Case4", 2, 0, "Action2", artefactProps.TYPE_VALUE_MISC, "dummy", os.path.join(self.testDataDir, "notExisitngFile.txt"))
 
        self.a_1 = artefactGenerator.generateArtefactEntry("Case1", 0, 1, "a1", "Type1", "Format1", "URL1", "Objctive1", myCoolProp = "Prop1")
        self.a_2 = artefactGenerator.generateArtefactEntry("Case2", 0, 2, "a2", "Type2", "Format2", "URL2", "Objctive2" )
        self.a_3 = artefactGenerator.generateArtefactEntry("Case3", None, 3, "a3", "Type3", "Format3", "URL3", "Objctive3", myCoolProp3 = "Prop3")

        self.session = workflow.Session("session1", self.sessionDir)
        self.session.artefacts.add_artefact(self.a_valid)
        self.session.artefacts.add_artefact(self.a_NoneURL)
        self.session.artefacts.add_artefact(self.a_NoFile)
        self.session.artefacts.add_artefact(self.a_Invalid)
        

    def tearDown(self):
        try:
            shutil.rmtree(self.sessionDir)
        except:
            pass
          
    def test_simelar_exisiting_alwaysDo(self):
      '''Test if always do enforces the computation/adding of an
      artefact even if a simelar exists.'''
      workflow.currentGeneratedSession = self.session
      action1 = DummySingleAction([self.a_valid_new],"Action1", True)
      
      action1.do()
      
      self.assertTrue(action1.isSuccess)
      self.assertIn(self.a_valid_new, action1.outputArtefacts)
      self.assertEqual(len(action1.outputArtefacts), 1)
      self.assertIn(action1,self.session.executed_actions)
      self.assertIn(self.a_valid_new, self.session.artefacts)
      self.assertFalse(self.session.artefacts.identical_artefact_exists(self.a_valid))
      self.assertEqual(action1.callCount_generateOutputs, 1)


    def test_simelar_exisiting_alwaysOff(self):
      '''test for similar existing artefact and alwaysDo == False
      => new artefact should not be added, status is "skipped".'''
      workflow.currentGeneratedSession = self.session
      action1 = DummySingleAction([self.a_valid_new],"Action1", False)
      
      action1.do()
      
      self.assertTrue(action1.isSkipped)
      self.assertIn(self.a_valid, action1.outputArtefacts)
      self.assertEqual(len(action1.outputArtefacts), 1)
      self.assertIn(action1,self.session.executed_actions)
      self.assertIn(self.a_valid, self.session.artefacts)
      self.assertFalse(self.session.artefacts.identical_artefact_exists(self.a_valid_new))
      self.assertEqual(action1.callCount_generateOutputs, 0)

    def test_simelar_mixed_exisiting_alwaysOff(self):
      '''test if action working directly if one artefact would skip and the other one won't'''
      workflow.currentGeneratedSession = self.session
      action1 = DummySingleAction([self.a_valid_new, self.a_NoneURL_new],"Action1", False)
      
      action1.do()
      
      self.assertTrue(action1.isSuccess)
      self.assertIn(self.a_valid_new, action1.outputArtefacts)
      self.assertIn(self.a_valid_new, action1.outputArtefacts)
      self.assertEqual(len(action1.outputArtefacts), 2)
      self.assertIn(action1,self.session.executed_actions)
      self.assertIn(self.a_valid_new, self.session.artefacts)
      self.assertFalse(self.session.artefacts.identical_artefact_exists(self.a_valid))
      self.assertIn(self.a_NoneURL_new, self.session.artefacts)
      self.assertFalse(self.session.artefacts.identical_artefact_exists(self.a_NoneURL))
      self.assertEqual(action1.callCount_generateOutputs, 1)

    def test_simelar_NoneURL_alwaysDo(self):
      '''test if action working directly if one artefact would skip and the other one won't'''
      workflow.currentGeneratedSession = self.session
      action1 = DummySingleAction([self.a_NoneURL_new],"Action1")
      
      action1.do()
      
      self.assertTrue(action1.isSuccess)
      self.assertIn(self.a_NoneURL_new, action1.outputArtefacts)
      self.assertEqual(len(action1.outputArtefacts), 1)
      self.assertIn(action1,self.session.executed_actions)
      self.assertIn(self.a_NoneURL_new, self.session.artefacts)
      self.assertFalse(self.session.artefacts.identical_artefact_exists(self.a_NoneURL))
      self.assertEqual(action1.callCount_generateOutputs, 1)

    def test_simelar_NoneURL_alwaysOff(self):
      '''test if simelar artefact with none URL is always overwritten.'''
      workflow.currentGeneratedSession = self.session
      action1 = DummySingleAction([self.a_NoneURL_new],"Action1", False)
      
      action1.do()
      
      self.assertTrue(action1.isSuccess)
      self.assertIn(self.a_NoneURL_new, action1.outputArtefacts)
      self.assertEqual(len(action1.outputArtefacts), 1)
      self.assertIn(action1,self.session.executed_actions)
      self.assertIn(self.a_NoneURL_new, self.session.artefacts)
      self.assertFalse(self.session.artefacts.identical_artefact_exists(self.a_NoneURL))
      self.assertEqual(action1.callCount_generateOutputs, 1)

    def test_simelar_not_exisiting_alwaysDo(self):
      '''test if simelar artefact with none URL is always overwritten.'''
      workflow.currentGeneratedSession = self.session
      action1 = DummySingleAction([self.a_NoFile_new],"Action1")
      
      action1.do()
      
      self.assertTrue(action1.isSuccess)
      self.assertIn(self.a_NoFile_new, action1.outputArtefacts)
      self.assertEqual(len(action1.outputArtefacts), 1)
      self.assertIn(action1,self.session.executed_actions)
      self.assertIn(self.a_NoFile_new, self.session.artefacts)
      self.assertFalse(self.session.artefacts.identical_artefact_exists(self.a_NoFile))

      
    def test_simelar_not_exisiting_alwaysOff(self):
      '''test if simelar artefact with non existant URL is always overwritten.'''
      workflow.currentGeneratedSession = self.session
      action1 = DummySingleAction([self.a_NoFile_new],"Action1", False)
      
      action1.do()
      
      self.assertTrue(action1.isSuccess)
      self.assertIn(self.a_NoFile_new, action1.outputArtefacts)
      self.assertEqual(len(action1.outputArtefacts), 1)
      self.assertIn(action1,self.session.executed_actions)
      self.assertIn(self.a_NoFile_new, self.session.artefacts)
      self.assertFalse(self.session.artefacts.identical_artefact_exists(self.a_NoFile))


    def test_simelar_invalid_alwaysDo(self):
      '''test if invalid simelar artefact is always overwritten.'''
      workflow.currentGeneratedSession = self.session
      action1 = DummySingleAction([self.a_Invalid_new],"Action1")
      
      action1.do()
      
      self.assertTrue(action1.isSuccess)
      self.assertIn(self.a_Invalid_new, action1.outputArtefacts)
      self.assertEqual(len(action1.outputArtefacts), 1)
      self.assertIn(action1,self.session.executed_actions)
      self.assertIn(self.a_Invalid_new, self.session.artefacts)
      self.assertFalse(self.session.artefacts.identical_artefact_exists(self.a_Invalid))

      
    def test_simelar_invalid_alwaysOff(self):
      '''test if invalid simelar artefact is always overwritten.'''
      workflow.currentGeneratedSession = self.session
      action1 = DummySingleAction([self.a_Invalid_new],"Action1", False)
      
      action1.do()
      
      self.assertTrue(action1.isSuccess)
      self.assertIn(self.a_Invalid_new, action1.outputArtefacts)
      self.assertEqual(len(action1.outputArtefacts), 1)
      self.assertIn(action1,self.session.executed_actions)
      self.assertIn(self.a_Invalid_new, self.session.artefacts)
      self.assertFalse(self.session.artefacts.identical_artefact_exists(self.a_Invalid))


    def test_new_alwaysDo(self):
      workflow.currentGeneratedSession = self.session
      action1 = DummySingleAction([self.a_valid2_new],"Action1")
      
      action1.do()
      
      self.assertTrue(action1.isSuccess)
      self.assertIn(self.a_valid2_new, action1.outputArtefacts)
      self.assertEqual(len(action1.outputArtefacts), 1)
      self.assertIn(action1,self.session.executed_actions)
      self.assertIn(self.a_valid2_new, self.session.artefacts)
      self.assertEqual(action1.callCount_generateOutputs, 1)

    def test_new_alwaysOff(self):
      workflow.currentGeneratedSession = self.session
      action1 = DummySingleAction([self.a_valid2_new],"Action1", False)
      
      action1.do()
      
      self.assertTrue(action1.isSuccess)
      self.assertIn(self.a_valid2_new, action1.outputArtefacts)
      self.assertEqual(len(action1.outputArtefacts), 1)
      self.assertIn(action1,self.session.executed_actions)
      self.assertIn(self.a_valid2_new, self.session.artefacts)
      self.assertEqual(action1.callCount_generateOutputs, 1)

    def test_invalidOutput(self):
      workflow.currentGeneratedSession = self.session
      action1 = DummySingleAction([self.a_NoFile2],"Action1")
      
      action1.do()
      
      self.assertTrue(action1.isFailure)
      self.assertIn(self.a_NoFile2, action1.outputArtefacts)
      self.assertTrue(action1.outputArtefacts[0][artefactProps.INVALID])
      self.assertEqual(len(action1.outputArtefacts), 1)
      self.assertIn(action1,self.session.executed_actions)
      self.assertIn(self.a_NoFile2, self.session.artefacts)
      self.assertIn(self.a_NoFile, self.session.artefacts)
      self.assertEqual(action1.callCount_generateOutputs, 1)

    def test_similar_but_new_misc_alwaysOff(self):
      '''Test if a new output that is not of type "result" triggers the action-
      It should not.'''
      workflow.currentGeneratedSession = self.session
      action1 = DummySingleAction([self.a_valid_new, self.a_NoResult],"Action1", False)
      
      action1.do()
      
      self.assertTrue(action1.isSkipped)
      self.assertIn(self.a_valid, action1.outputArtefacts)
      self.assertIn(action1,self.session.executed_actions)
      self.assertFalse(self.session.artefacts.identical_artefact_exists(self.a_valid_new))
      self.assertFalse(self.session.artefacts.identical_artefact_exists(self.a_NoResult))
      self.assertIn(self.a_valid, self.session.artefacts)

    def test_artefact_generation(self):
        workflow.currentGeneratedSession = workflow.Session("test_artefact_generation", self.sessionDir)

        action = DummySingleAction([self.a_1, self.a_2, self.a_3],"Test1")
        input_ids = {'i0': [self.a_1[artefactProps.ID]],'i1': [self.a_2[artefactProps.ID]],'i2': [self.a_3[artefactProps.ID]]}

        a = action.generateArtefact()
        ref = Artefact({'case': None, 'caseInstance': '0', 'format': None, 'url': None, 'timestamp': '1479379069.53',
                  'timePoint': None, 'actionTag': 'Test1', 'invalid': False, 'objective': None, 'type': None, 'result_sub_tag': None,
                  'id': 'e2c810cf-acb1-11e6-83b8-7054d2ab75be', 'input_ids':input_ids, artefactProps.ACTION_CLASS: 'DummySingleAction'}, {})
        self.assertTrue(ref.is_similar(a))
        self.assertDictEqual(input_ids, a[artefactProps.INPUT_IDS])

        a = action.generateArtefact(self.a_3)
        ref = Artefact({'case': 'Case3', 'caseInstance': '0', 'format': 'Format3', 'url': None, 'timestamp': '1479379250.0',
                  'timePoint': 3, 'actionTag': 'Test1', 'invalid': False, 'objective': 'Objctive3', 'type': 'Type3', 'result_sub_tag': None,
                  'id': '4e599a30-acb2-11e6-a3a0-7054d2ab75be', 'input_ids':input_ids, artefactProps.ACTION_CLASS: 'DummySingleAction'}, {'myCoolProp3': 'Prop3'})
        self.assertTrue(ref.is_similar(a))
        self.assertEqual(a['myCoolProp3'], ref['myCoolProp3'])
        self.assertDictEqual(input_ids, a[artefactProps.INPUT_IDS])

        a = action.generateArtefact(self.a_3, False)
        ref = Artefact({'case': 'Case3', 'caseInstance': '0', 'format': 'Format3', 'url': None, 'timestamp': '1479379309.88',
                  'timePoint': 3, 'actionTag': 'Test1', 'invalid': False, 'objective': 'Objctive3', 'type': 'Type3', 'result_sub_tag': None,
                  'id': '720a1b80-acb2-11e6-85a5-7054d2ab75be', 'input_ids':input_ids, artefactProps.ACTION_CLASS: 'DummySingleAction'}, {})
        self.assertTrue(ref.is_similar(a))
        self.assertTrue(not 'myCoolProp3' in a)
        self.assertDictEqual(input_ids, a[artefactProps.INPUT_IDS])

        #test additionalActionProps working
        action = DummySingleAction([self.a_1, self.a_2, self.a_3], "Test2", additionalActionProps={artefactProps.OBJECTIVE: 'newO'})
        a = action.generateArtefact(self.a_3)
        ref = Artefact({'case': 'Case3', 'caseInstance': '0', 'format': 'Format3', 'url': None, 'timestamp': '1479380425.43',
                  'timePoint': 3, 'actionTag': 'Test2', 'invalid': False, 'objective': 'newO', 'type': 'Type3', 'result_sub_tag': None,
                  'id': '0af4eb21-acb5-11e6-be37-7054d2ab75be', 'input_ids':input_ids, artefactProps.ACTION_CLASS: 'DummySingleAction'}, {'myCoolProp3': 'Prop3'})
        self.assertTrue(ref.is_similar(a))
        self.assertEqual(a['myCoolProp3'], ref['myCoolProp3'])
        self.assertDictEqual(input_ids, a[artefactProps.INPUT_IDS])

        #test propInheritanceDict working
        action = DummySingleAction([self.a_1, self.a_2, self.a_3], "Test3",
                                   propInheritanceDict={artefactProps.OBJECTIVE: 'i1', 'myCoolProp':'i0', 'notExistingProp':'i0', artefactProps.TIMEPOINT:'InexistingInput'})
        a = action.generateArtefact(self.a_3)
        ref = Artefact({'case': 'Case3', 'caseInstance': '0', 'format': 'Format3', 'url': None, 'timestamp': '1479380822.18',
                  'timePoint': 3, 'actionTag': 'Test3', 'invalid': False, 'objective': 'Objctive2', 'type': 'Type3', 'result_sub_tag': None,
                  'id': 'f771898f-acb5-11e6-b4db-7054d2ab75be', 'input_ids':input_ids, artefactProps.ACTION_CLASS: 'DummySingleAction'}, {'myCoolProp': 'Prop1', 'myCoolProp3': 'Prop3'})
        self.assertTrue(ref.is_similar(a))
        self.assertEqual(a['myCoolProp3'], ref['myCoolProp3'])
        self.assertEqual(a['myCoolProp'], ref['myCoolProp'])
        self.assertDictEqual(input_ids, a[artefactProps.INPUT_IDS])

        #test additionalActionProps overwrites propInheritanceDict
        action = DummySingleAction([self.a_1, self.a_2, self.a_3], "Test3",
                                   additionalActionProps={artefactProps.OBJECTIVE: 'newO'},
                                   propInheritanceDict={artefactProps.OBJECTIVE: 'i1', 'myCoolProp': 'i0', 'notExistingProp': 'i0',
                                                        artefactProps.TIMEPOINT: 'InexistingInput'})
        a = action.generateArtefact(self.a_3)
        ref = Artefact({'case': 'Case3', 'caseInstance': '0', 'format': 'Format3', 'url': None, 'timestamp': '1479381085.01',
                  'timePoint': 3, 'actionTag': 'Test3', 'invalid': False, 'objective': 'newO', 'type': 'Type3', 'result_sub_tag': None,
                  'id': '9419e84f-acb6-11e6-8b50-7054d2ab75be', 'input_ids':input_ids, artefactProps.ACTION_CLASS: 'DummySingleAction'}, {'myCoolProp3': 'Prop3', 'myCoolProp': 'Prop1'})
        self.assertTrue(ref.is_similar(a))
        self.assertEqual(a['myCoolProp3'], ref['myCoolProp3'])
        self.assertEqual(a['myCoolProp'], ref['myCoolProp'])
        self.assertDictEqual(input_ids, a[artefactProps.INPUT_IDS])

        #test auto url generation only prefix
        a = action.generateArtefact(self.a_3, url_user_defined_part="HumanReadableFileName")
        refURL = os.path.join(self.sessionDir, 'test_artefact_generation', 'Test3', 'Type3', 'Case3', '0', 'HumanReadableFileName.')
        refURL = refURL + a[artefactProps.ID]
        self.assertEqual(a[artefactProps.URL], refURL)

        #test auto url generation only extension
        a = action.generateArtefact(self.a_3, url_extension='txt')
        refURL = os.path.join(self.sessionDir, 'test_artefact_generation', 'Test3', 'Type3', 'Case3', '0', a[artefactProps.ID])
        refURL = refURL + os.extsep + 'txt'
        self.assertEqual(a[artefactProps.URL], refURL)

        #test auto url generation all
        a = action.generateArtefact(self.a_3, url_user_defined_part="HumanReadableFileName", url_extension='txt')
        refURL = os.path.join(self.sessionDir, 'test_artefact_generation', 'Test3', 'Type3', 'Case3', '0', 'HumanReadableFileName.')
        refURL = refURL + a[artefactProps.ID] + os.extsep + 'txt'
        self.assertEqual(a[artefactProps.URL], refURL)

        #test user defined props (overwritting everything)
        action = DummySingleAction([self.a_1, self.a_2, self.a_3], "Test3",
                                   additionalActionProps={artefactProps.OBJECTIVE: 'newO'},
                                   propInheritanceDict={artefactProps.OBJECTIVE: 'i1', 'myCoolProp': 'i0', 'notExistingProp': 'i0',
                                                        artefactProps.TIMEPOINT: 'InexistingInput'})
        a = action.generateArtefact(self.a_3, userDefinedProps={artefactProps.OBJECTIVE: 'userO', 'myUserProp': 'user1', 'myCoolProp': 'userCool',
                                                        artefactProps.TIMEPOINT: 42})
        ref = Artefact({'case': 'Case3', 'caseInstance': '0', 'format': 'Format3', 'url': None, 'timestamp': '1479381085.01',
                  'timePoint': 42, 'actionTag': 'Test3', 'invalid': False, 'objective': 'userO', 'type': 'Type3', 'result_sub_tag': None,
                  'id': '9419e84f-acb6-11e6-8b50-7054d2ab75be', 'input_ids':input_ids, artefactProps.ACTION_CLASS: 'DummySingleAction'}, {'myCoolProp': 'userCool', 'myUserProp':'user1'})
        self.assertTrue(ref.is_similar(a))
        self.assertEqual(a['myUserProp'], ref['myUserProp'])


    def test_invalid_inputs(self):
        '''Test if always do enforces the computation/adding of an
        artefact even if a simelar exists.'''
        workflow.currentGeneratedSession = self.session
        action1 = DummySingleAction([self.a_valid_new, self.a_NoFile], "Action1", True)

        action1.do()

        self.assertTrue(action1.isFailure)
        self.assertIn(self.a_valid_new, action1.outputArtefacts)
        self.assertFalse(self.session.artefacts.identical_artefact_exists(self.a_valid))
        self.assertIn(self.a_NoFile, action1.outputArtefacts)
        self.assertEqual(len(action1.outputArtefacts), 2)
        self.assertTrue(action1.outputArtefacts[0].is_invalid())
        self.assertTrue(action1.outputArtefacts[1].is_invalid())
        self.assertEqual(action1.callCount_generateOutputs, 0)

if __name__ == "__main__":
    unittest.main()