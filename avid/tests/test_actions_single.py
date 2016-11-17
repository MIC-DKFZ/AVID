
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
        self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary","test_actions")
        self.testDataDir = os.path.join(os.path.split(__file__)[0],"data")

        self.a_valid = artefactGenerator.generateArtefactEntry("Case1", 0, 0, "Action1", artefactProps.TYPE_VALUE_RESULT, "dummy", os.path.join(self.testDataDir, "artefact1.txt"))
        self.a_NoneURL = artefactGenerator.generateArtefactEntry("Case2", 1, 0, "Action1", artefactProps.TYPE_VALUE_RESULT, "dummy", None)
        self.a_NoFile = artefactGenerator.generateArtefactEntry("Case3", 1, 0, "Action1", artefactProps.TYPE_VALUE_RESULT, "dummy", "notexistingFile")
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
        self.a_3 = artefactGenerator.generateArtefactEntry("Case3", 1, 3, "a3", "Type3", "Format3", "URL3", "Objctive3", myCoolProp3 = "Prop3")

        self.session = workflow.Session("session1", self.sessionDir)
        artefact.addArtefactToWorkflowData(self.session.inData,self.a_valid)
        artefact.addArtefactToWorkflowData(self.session.inData,self.a_NoneURL)
        artefact.addArtefactToWorkflowData(self.session.inData,self.a_NoFile)
        artefact.addArtefactToWorkflowData(self.session.inData,self.a_Invalid)
        

    def tearDown(self):
        pass


    def testName(self):
        return "Test SingleActionBase"
      
          
    def test_simelar_exisiting_alwaysDo(self):
      '''Test if always do enforces the computation/adding of an
      artefact even if a simelar exists.'''
      workflow.currentGeneratedSession = self.session
      action1 = DummySingleAction([self.a_valid_new],"Action1", True)
      
      token = action1.do()
      
      self.assert_(token.isSuccess())
      self.assertIn(self.a_valid_new, token.generatedArtefacts)
      self.assertEqual(len(token.generatedArtefacts), 1)
      self.assertEqual(token.actionTag, action1.actionTag)
      self.assertEqual(self.session.actions[action1.actionTag], token)
      self.assertIn(self.a_valid_new, self.session.inData)
      

    def test_simelar_exisiting_alwaysOff(self):
      '''test for similar existing artefact and alwaysDo == False
      => new artefact should not be added, status is "skipped".'''
      workflow.currentGeneratedSession = self.session
      action1 = DummySingleAction([self.a_valid_new],"Action1", False)
      
      token = action1.do()
      
      self.assert_(token.isSkipped())
      self.assertIn(self.a_valid, token.generatedArtefacts)
      self.assertEqual(len(token.generatedArtefacts), 1)
      self.assertEqual(token.actionTag, action1.actionTag)
      self.assertEqual(self.session.actions[action1.actionTag], token)
      self.assertIn(self.a_valid, self.session.inData)
      self.assertFalse(self.a_valid_new in self.session.inData)


    def test_simelar_mixed_exisiting_alwaysOff(self):
      '''test if action working directly if one artefact would skip and the other one won't'''
      workflow.currentGeneratedSession = self.session
      action1 = DummySingleAction([self.a_valid_new, self.a_NoneURL_new],"Action1", False)
      
      token = action1.do()
      
      self.assert_(token.isSuccess())
      self.assertIn(self.a_valid_new, token.generatedArtefacts)
      self.assertIn(self.a_valid_new, token.generatedArtefacts)
      self.assertEqual(len(token.generatedArtefacts), 2)
      self.assertEqual(token.actionTag, action1.actionTag)
      self.assertEqual(self.session.actions[action1.actionTag], token)
      self.assertIn(self.a_valid_new, self.session.inData)
      self.assertFalse(self.a_valid in self.session.inData)
      self.assertIn(self.a_NoneURL_new, self.session.inData)
      self.assertFalse(self.a_NoneURL in self.session.inData)


    def test_simelar_NoneURL_alwaysDo(self):
      '''test if action working directly if one artefact would skip and the other one won't'''
      workflow.currentGeneratedSession = self.session
      action1 = DummySingleAction([self.a_NoneURL_new],"Action1")
      
      token = action1.do()
      
      self.assert_(token.isSuccess())
      self.assertIn(self.a_NoneURL_new, token.generatedArtefacts)
      self.assertEqual(len(token.generatedArtefacts), 1)
      self.assertEqual(token.actionTag, action1.actionTag)
      self.assertEqual(self.session.actions[action1.actionTag], token)
      self.assertIn(self.a_NoneURL_new, self.session.inData)

      
    def test_simelar_NoneURL_alwaysOff(self):
      '''test if simelar artefact with none URL is always overwritten.'''
      workflow.currentGeneratedSession = self.session
      action1 = DummySingleAction([self.a_NoneURL_new],"Action1", False)
      
      token = action1.do()
      
      self.assert_(token.isSuccess())
      self.assertIn(self.a_NoneURL_new, token.generatedArtefacts)
      self.assertEqual(len(token.generatedArtefacts), 1)
      self.assertEqual(token.actionTag, action1.actionTag)
      self.assertEqual(self.session.actions[action1.actionTag], token)
      self.assertIn(self.a_NoneURL_new, self.session.inData)


    def test_simelar_not_exisiting_alwaysDo(self):
      '''test if simelar artefact with none URL is always overwritten.'''
      workflow.currentGeneratedSession = self.session
      action1 = DummySingleAction([self.a_NoFile_new],"Action1")
      
      token = action1.do()
      
      self.assert_(token.isSuccess())
      self.assertIn(self.a_NoFile_new, token.generatedArtefacts)
      self.assertEqual(len(token.generatedArtefacts), 1)
      self.assertEqual(token.actionTag, action1.actionTag)
      self.assertEqual(self.session.actions[action1.actionTag], token)
      self.assertIn(self.a_NoFile_new, self.session.inData)

      
    def test_simelar_not_exisiting_alwaysOff(self):
      '''test if simelar artefact with non existant URL is always overwritten.'''
      workflow.currentGeneratedSession = self.session
      action1 = DummySingleAction([self.a_NoFile_new],"Action1", False)
      
      token = action1.do()
      
      self.assert_(token.isSuccess())
      self.assertIn(self.a_NoFile_new, token.generatedArtefacts)
      self.assertEqual(len(token.generatedArtefacts), 1)
      self.assertEqual(token.actionTag, action1.actionTag)
      self.assertEqual(self.session.actions[action1.actionTag], token)
      self.assertIn(self.a_NoFile_new, self.session.inData)


    def test_simelar_invalid_alwaysDo(self):
      '''test if invalid simelar artefact is always overwritten.'''
      workflow.currentGeneratedSession = self.session
      action1 = DummySingleAction([self.a_Invalid_new],"Action1")
      
      token = action1.do()
      
      self.assert_(token.isSuccess())
      self.assertIn(self.a_Invalid_new, token.generatedArtefacts)
      self.assertEqual(len(token.generatedArtefacts), 1)
      self.assertEqual(token.actionTag, action1.actionTag)
      self.assertEqual(self.session.actions[action1.actionTag], token)
      self.assertIn(self.a_Invalid_new, self.session.inData)

      
    def test_simelar_invalid_alwaysOff(self):
      '''test if invalid simelar artefact is always overwritten.'''
      workflow.currentGeneratedSession = self.session
      action1 = DummySingleAction([self.a_Invalid_new],"Action1", False)
      
      token = action1.do()
      
      self.assert_(token.isSuccess())
      self.assertIn(self.a_Invalid_new, token.generatedArtefacts)
      self.assertEqual(len(token.generatedArtefacts), 1)
      self.assertEqual(token.actionTag, action1.actionTag)
      self.assertEqual(self.session.actions[action1.actionTag], token)
      self.assertIn(self.a_Invalid_new, self.session.inData)
      

    def test_new_alwaysDo(self):
      workflow.currentGeneratedSession = self.session
      action1 = DummySingleAction([self.a_valid2_new],"Action1")
      
      token = action1.do()
      
      self.assert_(token.isSuccess())
      self.assertIn(self.a_valid2_new, token.generatedArtefacts)
      self.assertEqual(len(token.generatedArtefacts), 1)
      self.assertEqual(token.actionTag, action1.actionTag)
      self.assertEqual(self.session.actions[action1.actionTag], token)
      self.assertIn(self.a_valid2_new, self.session.inData)

      
    def test_new_alwaysOff(self):
      workflow.currentGeneratedSession = self.session
      action1 = DummySingleAction([self.a_valid2_new],"Action1", False)
      
      token = action1.do()
      
      self.assert_(token.isSuccess())
      self.assertIn(self.a_valid2_new, token.generatedArtefacts)
      self.assertEqual(len(token.generatedArtefacts), 1)
      self.assertEqual(token.actionTag, action1.actionTag)
      self.assertEqual(self.session.actions[action1.actionTag], token)
      self.assertIn(self.a_valid2_new, self.session.inData)


    def test_invalidOutput(self):
      workflow.currentGeneratedSession = self.session
      action1 = DummySingleAction([self.a_NoFile2],"Action1")
      
      token = action1.do()
      
      self.assert_(token.isFailure())
      self.assertIn(self.a_NoFile2, token.generatedArtefacts)
      self.assert_(token.generatedArtefacts[0][artefactProps.INVALID])
      self.assertEqual(len(token.generatedArtefacts), 1)
      self.assertEqual(token.actionTag, action1.actionTag)
      self.assertEqual(self.session.actions[action1.actionTag], token)
      self.assertIn(self.a_NoFile2, self.session.inData)


    def test_similar_but_new_misc_alwaysOff(self):
      '''Test if a new output that is not of type "result" triggers the action-
      It should not.'''
      workflow.currentGeneratedSession = self.session
      action1 = DummySingleAction([self.a_valid_new, self.a_NoResult],"Action1", False)
      
      token = action1.do()
      
      self.assert_(token.isSkipped())
      self.assertIn(self.a_valid, token.generatedArtefacts)
      self.assertEqual(len(token.generatedArtefacts), 1)
      self.assertEqual(self.session.actions[action1.actionTag], token)
      self.assertFalse(self.a_valid_new in self.session.inData)
      self.assertFalse(self.a_NoResult in self.session.inData)
      self.assertIn(self.a_valid, self.session.inData)

    def test_artefact_generation(self):
        workflow.currentGeneratedSession = workflow.Session("test_artefact_generation", self.sessionDir)

        action = DummySingleAction([self.a_1, self.a_2, self.a_3],"Test1")

        a = action.generateArtefact()
        ref = Artefact({'case': None, 'caseInstance': None, 'format': None, 'url': None, 'timestamp': '1479379069.53',
                  'timePoint': None, 'actionTag': 'Test1', 'invalid': False, 'objective': None, 'type': None,
                  'id': 'e2c810cf-acb1-11e6-83b8-7054d2ab75be'}, {})
        self.assert_(ref.is_similar(a))

        a = action.generateArtefact(self.a_3)
        ref = Artefact({'case': 'Case3', 'caseInstance': None, 'format': 'Format3', 'url': None, 'timestamp': '1479379250.0',
                  'timePoint': 3, 'actionTag': 'Test1', 'invalid': False, 'objective': 'Objctive3', 'type': 'Type3',
                  'id': '4e599a30-acb2-11e6-a3a0-7054d2ab75be'}, {'myCoolProp3': 'Prop3'})
        self.assert_(ref.is_similar(a))
        self.assertEqual(a['myCoolProp3'], ref['myCoolProp3'])

        a = action.generateArtefact(self.a_3, False)
        ref = Artefact({'case': 'Case3', 'caseInstance': None, 'format': 'Format3', 'url': None, 'timestamp': '1479379309.88',
                  'timePoint': 3, 'actionTag': 'Test1', 'invalid': False, 'objective': 'Objctive3', 'type': 'Type3',
                  'id': '720a1b80-acb2-11e6-85a5-7054d2ab75be'}, {})
        self.assert_(ref.is_similar(a))
        self.assert_(not 'myCoolProp3' in a)

        #test additionalActionProps working
        action = DummySingleAction([self.a_1, self.a_2, self.a_3], "Test2", additionalActionProps={artefactProps.OBJECTIVE: 'newO'})
        a = action.generateArtefact(self.a_3)
        ref = Artefact({'case': 'Case3', 'caseInstance': None, 'format': 'Format3', 'url': None, 'timestamp': '1479380425.43',
                  'timePoint': 3, 'actionTag': 'Test2', 'invalid': False, 'objective': 'newO', 'type': 'Type3',
                  'id': '0af4eb21-acb5-11e6-be37-7054d2ab75be'}, {'myCoolProp3': 'Prop3'})
        self.assert_(ref.is_similar(a))
        self.assertEqual(a['myCoolProp3'], ref['myCoolProp3'])

        #test propInheritanceDict working
        action = DummySingleAction([self.a_1, self.a_2, self.a_3], "Test3",
                                   propInheritanceDict={artefactProps.OBJECTIVE: 'i1', 'myCoolProp':'i0', 'notExistingProp':'i0', artefactProps.TIMEPOINT:'InexistingInput'})
        a = action.generateArtefact(self.a_3)
        ref = Artefact({'case': 'Case3', 'caseInstance': None, 'format': 'Format3', 'url': None, 'timestamp': '1479380822.18',
                  'timePoint': 3, 'actionTag': 'Test3', 'invalid': False, 'objective': 'Objctive2', 'type': 'Type3',
                  'id': 'f771898f-acb5-11e6-b4db-7054d2ab75be'}, {'myCoolProp': 'Prop1', 'myCoolProp3': 'Prop3'})
        self.assert_(ref.is_similar(a))
        self.assertEqual(a['myCoolProp3'], ref['myCoolProp3'])
        self.assertEqual(a['myCoolProp'], ref['myCoolProp'])

        #test additionalActionProps overwrites propInheritanceDict
        action = DummySingleAction([self.a_1, self.a_2, self.a_3], "Test3",
                                   additionalActionProps={artefactProps.OBJECTIVE: 'newO'},
                                   propInheritanceDict={artefactProps.OBJECTIVE: 'i1', 'myCoolProp': 'i0', 'notExistingProp': 'i0',
                                                        artefactProps.TIMEPOINT: 'InexistingInput'})
        a = action.generateArtefact(self.a_3)
        ref = Artefact({'case': 'Case3', 'caseInstance': None, 'format': 'Format3', 'url': None, 'timestamp': '1479381085.01',
                  'timePoint': 3, 'actionTag': 'Test3', 'invalid': False, 'objective': 'newO', 'type': 'Type3',
                  'id': '9419e84f-acb6-11e6-8b50-7054d2ab75be'}, {'myCoolProp3': 'Prop3', 'myCoolProp': 'Prop1'})
        self.assert_(ref.is_similar(a))
        self.assertEqual(a['myCoolProp3'], ref['myCoolProp3'])
        self.assertEqual(a['myCoolProp'], ref['myCoolProp'])

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()