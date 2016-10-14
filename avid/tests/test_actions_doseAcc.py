
import unittest
import os
import shutil
import avid.common.workflow as workflow
from avid.actions.doseAcc import DoseAccBatchAction as doseAcc
from avid.selectors.keyValueSelector import ActionTagSelector
from avid.sorter import BaseSorter

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


    def test_simple_dose_acc_action_alwaysdo(self):
      
      action = doseAcc(ActionTagSelector("Dose"), actionTag = "SimpleAcc", alwaysDo = True)      
      token = action.do()
      self.assertEqual(token.isSuccess(), True)
      token = action.do()
      self.assertEqual(token.isSuccess(), True)


if __name__ == "__main__":
    unittest.main()