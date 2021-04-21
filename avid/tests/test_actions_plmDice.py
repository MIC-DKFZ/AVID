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
from avid.actions.plmDice import PlmDiceBatchAction as plmDice
from avid.selectors.keyValueSelector import ActionTagSelector
import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper
from avid.common.AVIDUrlLocater import getToolConfigPath

@unittest.skipIf(getToolConfigPath('Plastimatch') is None, 'Tool Plastimatch not installed on the system.')
class TestPlmDice(unittest.TestCase):


    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "plmDiceTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "plmDiceTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_plmDice")
      
      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

              
    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_plm_dice_action(self):
      
      action = plmDice(ActionTagSelector("Target"), ActionTagSelector("Moving"), actionTag = "TestDice")      
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      refFilePath = os.path.join(self.testDataDir, "plmDice_Target_#0_vs_Moving_#1_ref.xml")
      resultFilePath = artefactHelper.getArtefactProperty(action._actions[0].outputArtefacts[0],
                                                      artefactProps.URL)
      with open(refFilePath) as refFile:
          with open(resultFilePath) as resultFile:
              self.assertEqual(refFile.read(), resultFile.read())

      refFilePath = os.path.join(self.testDataDir, "plmDice_Target_#0_vs_Moving_#2_ref.xml")
      resultFilePath = artefactHelper.getArtefactProperty(action._actions[1].outputArtefacts[0],
                                                      artefactProps.URL)
      with open(refFilePath) as refFile:
          with open(resultFilePath) as resultFile:
              self.assertEqual(refFile.read(), resultFile.read())

      token = action.do()
      self.assertEqual(token.isSkipped(), True)


    def test_simple_plm_dice_action_alwaysdo(self):
      
      action = plmDice(ActionTagSelector("Target"), ActionTagSelector("Moving"), alwaysDo = True, actionTag = "TestDice")      
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSuccess(), True)


if __name__ == "__main__":
    unittest.main()