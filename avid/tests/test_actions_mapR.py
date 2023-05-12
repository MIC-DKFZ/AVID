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
from avid.actions.mapR import mapRBatchAction as mapR
from avid.common.artefact.defaultProps import TIMEPOINT
from avid.linkers import CaseLinker
from avid.selectors.keyValueSelector import ActionTagSelector

from avid.common.AVIDUrlLocater import getToolConfigPath

@unittest.skipIf(getToolConfigPath('mapR') is None, 'Tool mapR not installed on the system.')
class TestMapR(unittest.TestCase):


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

    def test_simple_mapr_action(self):
      
      action = mapR(ActionTagSelector("Moving"), ActionTagSelector("Registration"), ActionTagSelector("Target"), actionTag = "TestMapping")      
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSkipped(), True)


    def test_simple_mapr_action_alwaysdo(self):
      
      action = mapR(ActionTagSelector("Moving"), ActionTagSelector("Registration"), ActionTagSelector("Target"), alwaysDo = True, actionTag = "TestMapping_alwaysdo")
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSuccess(), True)

    def test_mapr_action_caselinking(self):

        action = mapR(ActionTagSelector("Moving"), ActionTagSelector("Registration"), ActionTagSelector("Target"),
                      regLinker= CaseLinker(), actionTag = "TestMapping_caselinking")
        token = action.do()

        self.assertEqual(token.isSuccess(), True)

        token = action.do()
        self.assertEqual(token.isSkipped(), True)

    def test_mapr_action_inputIsReference(self):

        newsession = workflow.initSession(os.path.join(self.sessionDir, "testlist_2.avid"), expandPaths=True,
                                            bootstrapArtefacts=self.testArtefactFile2)

        action = mapR(ActionTagSelector("Moving"), ActionTagSelector("Registration"), ActionTagSelector("Target"),
                      alwaysDo=True, actionTag="TestMapping_inputIsReference")
        token = action.do()
        self.assertEqual(token.isSuccess(), True)
        self.assertEqual(token.generatedArtefacts[0][TIMEPOINT], 1)

        action = mapR(ActionTagSelector("Moving"), ActionTagSelector("Registration"), ActionTagSelector("Target"),
                      inputIsReference=False, alwaysDo=True, actionTag="TestMapping_inputIsReference")
        token = action.do()
        self.assertEqual(token.isSuccess(), True)
        #now the template should be reference for output artefacts, thus the time point should be 0 (timpoint of
        #the template
        self.assertEqual(token.generatedArtefacts[0][TIMEPOINT], 0)


if __name__ == "__main__":
    unittest.main()