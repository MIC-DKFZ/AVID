
import unittest
import avid.common.workflow as workflow
import os
from avid.actions.dummy import DummySingleAction
import avid.common.artefact.generator as artefactGenerator
import avid.common.artefact as artefact
import avid.common.artefact.defaultProps as artefactProps

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
      '''test for similar existing artefact and alwaysDo == False'''
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
      
      
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()