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
from avid.actions.plmCompare import plmCompareBatchAction as plmCompare
from avid.selectors.keyValueSelector import ActionTagSelector
import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper

class TestPlmCompare(unittest.TestCase):


    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "plmCompareTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "plmCompareTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_plmCompare")
      
      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

              
    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_plm_compare_action(self):
      
      action = plmCompare(ActionTagSelector("Target"), ActionTagSelector("Moving"), actionTag = "TestCompare")      
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      refFile = os.path.join(self.testDataDir, "plmCompare_Target_#0_vs_Moving_#1_ref.xml")
      resultFile = artefactHelper.getArtefactProperty(action._actions[0]._resultArtefact,
                                                      artefactProps.URL)
      self.assertEqual(open(refFile).read(), open(resultFile).read())

      refFile = os.path.join(self.testDataDir, "plmCompare_Target_#0_vs_Moving_#2_ref.xml")
      resultFile = artefactHelper.getArtefactProperty(action._actions[1]._resultArtefact,
                                                      artefactProps.URL)
      self.assertEqual(open(refFile).read(), open(resultFile).read())

      token = action.do()
      self.assertEqual(token.isSkipped(), True)


    def test_simple_plm_compare_action_alwaysdo(self):
      
      action = plmCompare(ActionTagSelector("Target"), ActionTagSelector("Moving"), alwaysDo = True, actionTag = "TestCompare")      
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSuccess(), True)


if __name__ == "__main__":
    unittest.main()