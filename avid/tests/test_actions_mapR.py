
import unittest
import os
import shutil
import avid.common.workflow as workflow
from avid.actions.mapR import mapRBatchAction as mapR
from avid.selectors.keyValueSelector import ActionTagSelector

class TestMapR(unittest.TestCase):


    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "mapRTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "maprTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary","test_mapr")
      
      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

              
    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_mapr_action(self):
      
      action = mapR(ActionTagSelector("Moving"), ActionTagSelector("Registration"), ActionTagSelector("Target"), actionTag = "TestMapping")      
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSkipped(), True)


    def test_simple_mapr_action_alwaysdo(self):
      
      action = mapR(ActionTagSelector("Moving"), ActionTagSelector("Registration"), ActionTagSelector("Target"), alwaysDo = True, actionTag = "TestMapping")      
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSuccess(), True)


if __name__ == "__main__":
    unittest.main()