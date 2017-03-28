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
from avid.actions.regVarTool import RegVarToolBatchAction as regVarTool
from avid.selectors.keyValueSelector import ActionTagSelector
from avid.selectors import FormatSelector
from avid.common import AVIDUrlLocater
from avid.common.AVIDUrlLocater import getToolConfigPath

@unittest.skipIf(getToolConfigPath('RegVarTool') is None, 'Tool RegVarTool not installed on the system.')
class TestRegVarTool(unittest.TestCase):


    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "regVarToolTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "mapRTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_regVarTool")
      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

      self.numberOfVariations = 3
      self.algorithmDLLEuler = os.path.join(AVIDUrlLocater.getUtilityPath(), "RegVarTool", "mdra-0-12_RegVariationRandomGaussianEuler.dll")
      self.algorithmDLLTPS = os.path.join(AVIDUrlLocater.getUtilityPath(), "RegVarTool", "mdra-0-12_RegVariationKernelRandomGaussianTPS.dll")
      self.parameters = {"MeanGlobal" : "0.0", "StandardDeviationGlobal" : "1.0", "Seed" : "0"}

              
    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_regvartool_action(self):
      action = regVarTool(ActionTagSelector("Registration")+FormatSelector("MatchPoint"), self.numberOfVariations, algorithmDLL = self.algorithmDLLEuler, actionTag = "TestRegVar")
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSkipped(), True)


    def test_simple_regvar_action_alwaysdo(self):
      
      action = regVarTool(ActionTagSelector("Registration")+FormatSelector("MatchPoint"), self.numberOfVariations, algorithmDLL = self.algorithmDLLEuler, alwaysDo = True, actionTag = "TestRegVar")
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSuccess(), True)

    def test_simple_regvar_action_parameters(self):
      action = regVarTool(ActionTagSelector("Registration") + FormatSelector("MatchPoint"), self.numberOfVariations,
                          algorithmDLL=self.algorithmDLLEuler, parameters = self.parameters, actionTag="TestRegVarParam")
      token = action.do()

      self.assertEqual(token.isSuccess(), True)

    def test_simple_regvar_action_image(self):
      action = regVarTool(ActionTagSelector("Registration") + FormatSelector("MatchPoint"), self.numberOfVariations,
                          algorithmDLL=self.algorithmDLLTPS, templateSelector=ActionTagSelector("Target"), actionTag="TestRegVarImage")
      token = action.do()

      self.assertEqual(token.isSuccess(), True)


if __name__ == "__main__":
    unittest.main()