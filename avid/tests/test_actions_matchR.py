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

import os
import shutil
import unittest

import avid.common.workflow as workflow
from avid.actions.matchR import matchRBatchAction as matchR
from avid.common.AVIDUrlLocater import getUtilityPath
from avid.selectors.keyValueSelector import ActionTagSelector
from avid.common.AVIDUrlLocater import getToolConfigPath

@unittest.skipIf(getToolConfigPath('matchR') is None, 'Tool matchR not installed on the system.')
class TestMatchR(unittest.TestCase):


    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "matchRTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "matchRTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary","test_matchR")

      self.dllPath = os.path.join(getUtilityPath(), "matchR")
      self.itkAlgorithm = os.path.join(self.dllPath, "mdra-0-12_ITKEuler3DMattesMIMultiRes.dll")
      
      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

              
    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_reg_action(self):
      
      action = matchR(ActionTagSelector("Target"), ActionTagSelector("Moving"), algorithm = self.itkAlgorithm, actionTag = "TestReg")
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSkipped(), True)


    def test_simple_reg_action_always_do(self):
      
      action = matchR(ActionTagSelector("Target"), ActionTagSelector("Moving"), algorithm = self.itkAlgorithm, actionTag = "TestReg", alwaysDo = True)
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSuccess(), True)


if __name__ == "__main__":
    unittest.main()