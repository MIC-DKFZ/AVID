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
from avid.actions.MitkMapImageMiniApp import MitkMapImageMiniAppBatchAction as map
from avid.common.artefact.defaultProps import TIMEPOINT
from avid.linkers import CaseLinker
from avid.selectors.keyValueSelector import ActionTagSelector

from avid.common.AVIDUrlLocater import getToolConfigPath

@unittest.skipIf(getToolConfigPath('MitkMapImageMiniApp') is None, 'Tool MitkMapImageMiniApp not installed on the system.')
class TestMitkMapImageMiniApp(unittest.TestCase):


    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "mapRTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "mapRTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_MitkMapImageMiniApp")
      self.testArtefactFile2 = os.path.join(os.path.split(__file__)[0],"data", "mapRTest", "testlist_2.avid")

      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

              
    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_MitkMapImageMiniApp_action(self):
      
      action = map(ActionTagSelector("Moving"), ActionTagSelector("Registration"), ActionTagSelector("Target"), actionTag = "TestMapping")
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSkipped(), True)


    def test_simple_MitkMapImageMiniApp_action_alwaysdo(self):
      
      action = map(ActionTagSelector("Moving"), ActionTagSelector("Registration"), ActionTagSelector("Target"), alwaysDo = True, actionTag = "TestMapping_alwaysdo")
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSuccess(), True)

    def test_MitkMapImageMiniApp_action_caselinking(self):

        action = map(ActionTagSelector("Moving"), ActionTagSelector("Registration"), ActionTagSelector("Target"),
                      regLinker= CaseLinker(), actionTag = "TestMapping_caselinking")
        token = action.do()

        self.assertEqual(token.isSuccess(), True)

        token = action.do()
        self.assertEqual(token.isSkipped(), True)

    def test_MitkMapImageMiniApp_action_inputIsReference(self):

        newsession = workflow.initSession(os.path.join(self.sessionDir, "testlist_2.avid"), expandPaths=True,
                                            bootstrapArtefacts=self.testArtefactFile2)

        action = map(ActionTagSelector("Moving"), ActionTagSelector("Registration"), ActionTagSelector("Target"),
                      alwaysDo=True, actionTag="TestMapping")
        token = action.do()
        self.assertEqual(token.isSuccess(), True)
        self.assertEqual(token.generatedArtefacts[0][TIMEPOINT], 1)

        action = map(ActionTagSelector("Moving"), ActionTagSelector("Registration"), ActionTagSelector("Target"),
                      inputIsArtefactReference=False, alwaysDo=True, actionTag="TestMapping")
        token = action.do()
        self.assertEqual(token.isSuccess(), True)
        #now the template should be reference for output artefacts, thus the time point should be 0 (timpoint of
        #the template
        self.assertEqual(token.generatedArtefacts[0][TIMEPOINT], 0)

    def test_MitkMapImageMiniApp_action_supersampling(self):

        action = map(ActionTagSelector("Moving"), ActionTagSelector("Registration"), ActionTagSelector("Target"),
                     supersamplingFactor = 3, actionTag = "TestMapping_1ss")
        token = action.do()

        self.assertEqual(token.isSuccess(), True)

    def test_MitkMapImageMiniApp_action_supersampling3(self):

        action = map(ActionTagSelector("Moving"), ActionTagSelector("Registration"), ActionTagSelector("Target"),
                     supersamplingFactor = [3,2,1], actionTag = "TestMapping_3ss")
        token = action.do()

        self.assertEqual(token.isSuccess(), True)


if __name__ == "__main__":
    unittest.main()