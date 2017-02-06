# AVID
# Automated workflow system for cohort analysis in radiology and radiation therapy
#
# Copyright (c) German Cancer Research Center,
# Software development for Integrated Diagnostic and Therapy (SIDT).
# All rights reserved.
#
# This software is distributed WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.
#
# See LICENSE.txt or http://www.dkfz.de/en/sidt/index.html for details.

import unittest
import os
import shutil
import avid.common.workflow as workflow
from avid.actions.voxelizer import VoxelizerBatchAction as voxelizer
from avid.selectors.keyValueSelector import ActionTagSelector
from avid.common.AVIDUrlLocater import getToolConfigPath

@unittest.skipIf(getToolConfigPath('VoxelizerTool') is None, 'Tool VoxelizerTool not installed on the system.')
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

    def test_simple_action(self):
      
      action = voxelizer(ActionTagSelector('Struct'), ActionTagSelector('Reference'),
                         ['Heart'], actionTag = "TestVoxelizer")
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSkipped(), True)

    def test_simple_action_session_struct(self):
      
      action = voxelizer(ActionTagSelector('Struct'), ActionTagSelector('Reference'),
                         actionTag = "TestVoxelizer", alwaysDo = True)
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

    def test_simple_action_boolean(self):
      
      action = voxelizer(ActionTagSelector('Struct'), ActionTagSelector('Reference'),
                         booleanMask = True, actionTag = "TestVoxelizer", alwaysDo = True)
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

    def test_simple_action_alwaysdo(self):
      
      action = voxelizer(ActionTagSelector('Struct'), ActionTagSelector('Reference'),
                         ['Heart'], actionTag = "TestVoxelizer", alwaysDo = True)
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSuccess(), True)


if __name__ == "__main__":
    unittest.main()