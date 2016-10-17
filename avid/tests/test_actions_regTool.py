
import unittest
import os
import shutil
import avid.common.workflow as workflow
from avid.actions.regTool import regToolBatchAction as regTool
from avid.selectors.keyValueSelector import ActionTagSelector
from avid.common import AVIDUrlLocater
import avid.common.templateFileCustomizer as templateFileCustomizer

class TestRegTool(unittest.TestCase):


    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "regToolTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "regToolTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_regTool")
      self.templatePath = os.path.join(os.path.split(__file__)[0],"data", "regToolTest",  "test_config.reg.xml")
      self.confTemplatePath = os.path.join(self.sessionDir,"test_config.reg.xml")
      self.dllPath = os.path.dirname(AVIDUrlLocater.getToolConfigPath('RegTool'))
          
      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

      replaceDict = {'@ReleaseDllPath@': self.dllPath,
                     "@ReleaseDll@": "mdra-0-11_ITKEuler3DMattesMIMultiRes.dll"}
      templateFileCustomizer.writeFileCustomized(self.templatePath, self.confTemplatePath,replaceDict )      

              
    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_reg_action(self):
      
      action = regTool(ActionTagSelector("Target"), ActionTagSelector("Moving"), self.confTemplatePath, actionTag = "TestReg")     
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSkipped(), True)


    def test_simple_reg_action_allways_do(self):
      
      action = regTool(ActionTagSelector("Target"), ActionTagSelector("Moving"), self.confTemplatePath, actionTag = "TestReg", alwaysDo = True)     
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSuccess(), True)


if __name__ == "__main__":
    unittest.main()