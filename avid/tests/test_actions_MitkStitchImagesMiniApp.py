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
from avid.actions.MitkStitchImagesMiniApp import MitkStitchImagesMiniAppBatchAction as stitch
from avid.common.artefact.defaultProps import TIMEPOINT
from avid.selectors.keyValueSelector import ActionTagSelector

from avid.common.AVIDUrlLocater import getToolConfigPath

@unittest.skipIf(getToolConfigPath('MitkStitchImagesMiniApp') is None, 'Tool MitkStitchImagesMiniApp not installed on the system.')
class TestMitkStitchImagesMiniApp(unittest.TestCase):

    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "mapRTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "mapRTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_mapr")
      self.testArtefactFile2 = os.path.join(os.path.split(__file__)[0],"data", "mapRTest", "testlist_2.avid")

      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

              
    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_stitch_action(self):
      
      action = stitch(ActionTagSelector("Moving"), ActionTagSelector("Target"), ActionTagSelector("Registration"), actionTag = "TestStitch")
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSkipped(), True)

      action = stitch(ActionTagSelector("Moving"), ActionTagSelector("Target"),
                      actionTag="TestStitch")
      token = action.do()

      self.assertEqual(token.isSuccess(), True)

    def test_simple_stitch_action_alwaysdo(self):
      
      action = stitch(ActionTagSelector("Moving"), ActionTagSelector("Target"), ActionTagSelector("Registration"), alwaysDo = True, actionTag = "TestStitch")
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSuccess(), True)


if __name__ == "__main__":
    unittest.main()