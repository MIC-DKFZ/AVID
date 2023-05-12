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
from avid.actions.combineR import combineRBatchAction as combineR
from avid.common.artefact.defaultProps import TIMEPOINT
from avid.selectors.keyValueSelector import ActionTagSelector

from avid.common.AVIDUrlLocater import getToolConfigPath

@unittest.skipIf(getToolConfigPath('combineR') is None, 'Tool combineR not installed on the system.')
class TestMapR(unittest.TestCase):


    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "combineRTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "combineRTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_mapr")

      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

              
    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_combiner_action(self):
      
      action = combineR(ActionTagSelector("reg1"), ActionTagSelector("reg2"), actionTag = "TestCombination")
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSkipped(), True)


    def test_simple_combiner_action_alwaysdo(self):

      action = combineR(ActionTagSelector("reg1"), ActionTagSelector("reg2"), alwaysDo=True, actionTag = "TestCombination_alwaysDo")
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSuccess(), True)


if __name__ == "__main__":
    unittest.main()