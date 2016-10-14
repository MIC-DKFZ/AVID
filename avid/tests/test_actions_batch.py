import unittest
import avid.common.workflow as workflow
import os
from avid.actions.dummy import DummyBatchAction
from avid.actions import BatchActionBase
import avid.common.artefact.generator as artefactGenerator
import avid.common.artefact as artefact
import avid.common.artefact.defaultProps as artefactProps
from avid.selectors.keyValueSelector import CaseSelector

class Test(unittest.TestCase):

    def setUp(self):
        self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary","test_actions")
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
        artefact.addArtefactToWorkflowData(self.session.inData,self.a_valid)
        artefact.addArtefactToWorkflowData(self.session.inData,self.a_valid2)
        artefact.addArtefactToWorkflowData(self.session.inData,self.a_NoneURL)
        artefact.addArtefactToWorkflowData(self.session.inData,self.a_NoFile)
        artefact.addArtefactToWorkflowData(self.session.inData,self.a_Invalid)
        

    def tearDown(self):
        pass


    def testName(self):
        return "Test BatchActionBase"

        
    def test_simelar_exisiting_alwaysDo(self):
      workflow.currentGeneratedSession = self.session
      action = DummyBatchAction([self.a_valid_new, self.a_valid2_new],"Action1", True)
      
      token = action.do()
      
      self.assert_(token.isSuccess())
      self.assertIn(self.a_valid_new, token.generatedArtefacts)
      self.assertIn(self.a_valid2_new, token.generatedArtefacts)
      self.assertEqual(len(token.generatedArtefacts), 2)
      self.assertEqual(token.actionTag, action.actionTag)
      self.assertEqual(self.session.actions[action.actionTag], token)
      self.assertIn(self.a_valid_new, self.session.inData)
      self.assertIn(self.a_valid2_new, self.session.inData)
      

    def test_simelar_exisiting_alwaysOff(self):
      workflow.currentGeneratedSession = self.session
      action = DummyBatchAction([self.a_valid_new, self.a_valid2_new],"Action1", False)
      
      token = action.do()
      
      self.assert_(token.isSkipped())
      self.assertIn(self.a_valid, token.generatedArtefacts)
      self.assertIn(self.a_valid2, token.generatedArtefacts)
      self.assertEqual(len(token.generatedArtefacts), 2)
      self.assertEqual(token.actionTag, action.actionTag)
      self.assertEqual(self.session.actions[action.actionTag], token)
      self.assertIn(self.a_valid, self.session.inData)
      self.assertIn(self.a_valid2, self.session.inData)
      self.assertFalse(self.a_valid_new in self.session.inData)
      self.assertFalse(self.a_valid2_new in self.session.inData)


    def test_simelar_mixed_alwaysDo(self):
      workflow.currentGeneratedSession = self.session
      action = DummyBatchAction([self.a_valid_new, self.a_Invalid_new],"Action1", True)
      
      token = action.do()
      
      self.assert_(token.isSuccess())
      self.assertIn(self.a_valid_new, token.generatedArtefacts)
      self.assertIn(self.a_Invalid_new, token.generatedArtefacts)
      self.assertEqual(len(token.generatedArtefacts), 2)
      self.assertEqual(token.actionTag, action.actionTag)
      self.assertEqual(self.session.actions[action.actionTag], token)
      self.assertIn(self.a_valid_new, self.session.inData)
      self.assertIn(self.a_Invalid_new, self.session.inData)


    def test_simelar_mixed_alwaysOff(self):
      workflow.currentGeneratedSession = self.session
      action = DummyBatchAction([self.a_valid_new, self.a_Invalid_new],"Action1", False)
      
      token = action.do()
      
      self.assert_(token.isSuccess())
      self.assertIn(self.a_valid, token.generatedArtefacts)
      self.assertIn(self.a_Invalid_new, token.generatedArtefacts)
      self.assertEqual(len(token.generatedArtefacts), 2)
      self.assertEqual(token.actionTag, action.actionTag)
      self.assertEqual(self.session.actions[action.actionTag], token)
      self.assertIn(self.a_valid, self.session.inData)
      self.assertIn(self.a_Invalid_new, self.session.inData)
      self.assertFalse(self.a_valid_new in self.session.inData)
      self.assertFalse(self.a_Invalid in self.session.inData)


    def test_failure_mixed_alwaysOn(self):
      workflow.currentGeneratedSession = self.session
      action = DummyBatchAction([self.a_valid_new, self.a_NoFile],"Action1", True)
      
      token = action.do()
      
      self.assert_(token.isFailure())
      self.assertIn(self.a_valid_new, token.generatedArtefacts)
      self.assertIn(self.a_NoFile, token.generatedArtefacts)
      self.assertEqual(len(token.generatedArtefacts), 2)
      self.assertEqual(token.actionTag, action.actionTag)
      self.assertEqual(self.session.actions[action.actionTag], token)
      self.assertIn(self.a_valid_new, self.session.inData)
      self.assertIn(self.a_NoFile, self.session.inData)
      self.assert_(token.generatedArtefacts[1][artefactProps.INVALID])

    
    def test_failure_mixed_alwaysOff(self):
      workflow.currentGeneratedSession = self.session
      action = DummyBatchAction([self.a_valid_new, self.a_NoFile],"Action1")
      
      token = action.do()
      
      self.assert_(token.isFailure())
      self.assertIn(self.a_valid, token.generatedArtefacts)
      self.assertIn(self.a_NoFile, token.generatedArtefacts)
      self.assertEqual(len(token.generatedArtefacts), 2)
      self.assertEqual(token.actionTag, action.actionTag)
      self.assertEqual(self.session.actions[action.actionTag], token)
      self.assertIn(self.a_valid, self.session.inData)
      self.assertIn(self.a_NoFile, self.session.inData)
      self.assert_(token.generatedArtefacts[1][artefactProps.INVALID])


    def test_ensure_valid_artifacts(self):
      workflow.currentGeneratedSession = self.session
      action = BatchActionBase("Action1")
      
      selection = action.ensureValidArtefacts(self.session.inData)
     
      self.assert_(len(selection)==4)
      self.assertIn(self.a_valid, selection)
      self.assertIn(self.a_valid2, selection)
      self.assertIn(self.a_NoneURL, selection)
      self.assertIn(self.a_NoFile, selection)

      
    def test_ensure_valid_artifacts_additional_selector(self):
      workflow.currentGeneratedSession = self.session
      action = BatchActionBase("Action1")
      
      selection = action.ensureValidArtefacts(self.session.inData, CaseSelector("Case2"))
     
      self.assert_(len(selection)==2)
      self.assertIn(self.a_valid2, selection)
      self.assertIn(self.a_NoneURL, selection)
      

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()