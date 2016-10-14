import unittest
import os
from avid.actions import ActionBase
import avid.common.artefact.generator as artefactGenerator
import avid.common.artefact as artefact
import avid.common.workflow as workflow

class Test(unittest.TestCase):

    def setUp(self):
        self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary","test_actions")
        self.testDataDir = os.path.join(os.path.split(__file__)[0],"data")

        self.a1 = artefactGenerator.generateArtefactEntry("Case1", 0, 0, "Action1", "result", "dummy", os.path.join(self.testDataDir, "artefact1.txt"))
        self.a2 = artefactGenerator.generateArtefactEntry("Case2", 1, 0, "Action1", "misc", "dummy", None)
        self.a3 = artefactGenerator.generateArtefactEntry("Case3", 1, 0, "Action1", "misc", "dummy", "notexistingFile")
        self.a4 = artefactGenerator.generateArtefactEntry("Case2", 2, 0, "Action1", "misc", "dummy", os.path.join(self.testDataDir, "artefact2.txt"), invalid = True)
        
        self.session = workflow.Session("session1", self.sessionDir)
        artefact.addArtefactToWorkflowData(self.session.inData,self.a1)
        artefact.addArtefactToWorkflowData(self.session.inData,self.a2)
        artefact.addArtefactToWorkflowData(self.session.inData,self.a3)
        artefact.addArtefactToWorkflowData(self.session.inData,self.a4)
        
        self.session2 = workflow.Session("session2", self.sessionDir)
        artefact.addArtefactToWorkflowData(self.session2.inData,self.a1)


    def tearDown(self):
        pass


    def testName(self):
        return "Test basic actions"

    
    def test_ActionBase(self):

      action = ActionBase("Action1",self.session)
      self.assertEqual(action._actionTag, "Action1")
      self.assertEqual(action._session, self.session)
      
      workflow.currentGeneratedSession = None

      with self.assertRaises(ValueError):
        ActionBase("Action2")
        
      workflow.currentGeneratedSession = self.session2
      
      action3 = ActionBase("Action3")
      self.assertEqual(action3._actionTag, "Action3")
      self.assertEqual(action3._session, self.session2)
      
      with self.assertRaises(NotImplementedError):
        action3.indicateOutputs()
        
      with self.assertRaises(NotImplementedError):
        action3._do()

      with self.assertRaises(NotImplementedError):
        action3.do()
      
      
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()