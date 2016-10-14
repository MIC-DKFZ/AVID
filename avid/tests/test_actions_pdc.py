
import unittest
import os
import shutil
import avid.common.workflow as workflow
from avid.actions.pdc import pdcBatchAction as pdc
from avid.selectors.keyValueSelector import ActionTagSelector

class TestPDC(unittest.TestCase):


    def setUp(self):
      
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "pdcTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "pdcTest", "testlist.avid")
            
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_pdc")

      self.batPath = os.path.join(os.path.split(__file__)[0],"data", "pdcTest", "PDC_template.bat")
         
      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

              
    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_pdc_action(self):
      
      action = pdc(ActionTagSelector("BPLCT"), ActionTagSelector("Plan"), ActionTagSelector("Struct"), actionTag = "TestPDC", executionBat = self.batPath)     
      token = action.do()
      self.assertEqual(token.isSuccess(), True)


if __name__ == "__main__":
    unittest.main()