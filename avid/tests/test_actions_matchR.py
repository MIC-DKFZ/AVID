import os
import shutil
import unittest

import avid.common.workflow as workflow
from avid.actions.matchR import matchRBatchAction as matchR
from avid.common.AVIDUrlLocater import getAVIDRootPath
from avid.selectors.keyValueSelector import ActionTagSelector


class TestMatchR(unittest.TestCase):


    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "matchRTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "matchRTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_matchR")
      self.dllPath = os.path.join(getAVIDRootPath(), "Utilities", "matchR")
      self.itkAlgorithm = os.path.join(self.dllPath, "mdra-0-12_ITKEuler3DMattesMIMultiRes.dll")
      
      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

              
    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_reg_action(self):
      
      action = matchR(ActionTagSelector("Target"), ActionTagSelector("Moving"), self.itkAlgorithm, actionTag = "TestReg")
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSkipped(), True)


    def test_simple_reg_action_always_do(self):
      
      action = matchR(ActionTagSelector("Target"), ActionTagSelector("Moving"), self.itkAlgorithm, actionTag = "TestReg", alwaysDo = True)
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSuccess(), True)


if __name__ == "__main__":
    unittest.main()