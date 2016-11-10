
import unittest
import os
import shutil
import avid.common.workflow as workflow
from avid.actions.voxelizer import VoxelizerBatchAction as voxelizer
from avid.selectors.keyValueSelector import ActionTagSelector

class TestVoxelizer(unittest.TestCase):


    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "voxelizerTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "voxelizerTest", "testlist.avid")
      self.testStructDef = os.path.join(os.path.split(__file__)[0],"data", "voxelizerTest", "structdef.xml")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_voxelizer")
      
      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"),
                                          expandPaths=True, bootstrapArtefacts=self.testArtefactFile,
                                          structDefinition = self.testStructDef)

    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_mapr_action(self):
      
      action = voxelizer(ActionTagSelector('Reference'), ActionTagSelector('Struct'),
                         ['Brain'], actionTag = "TestVoxelizer")
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSkipped(), True)

    def test_simple_mapr_action_session_struct(self):
      
      action = voxelizer(ActionTagSelector('Reference'), ActionTagSelector('Struct'),
                         actionTag = "TestVoxelizer", alwaysDo = True)
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

    def test_simple_mapr_action_boolean(self):
      
      action = voxelizer(ActionTagSelector('Reference'), ActionTagSelector('Struct'),
                         booleanMask = True, actionTag = "TestVoxelizer", alwaysDo = True)
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

    def test_simple_mapr_action_alwaysdo(self):
      
      action = voxelizer(ActionTagSelector('Reference'), ActionTagSelector('Struct'),
                         ['Brain'], actionTag = "TestVoxelizer", alwaysDo = True)
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSuccess(), True)


if __name__ == "__main__":
    unittest.main()