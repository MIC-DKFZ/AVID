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
from avid.actions.MRPerfusionMiniApp import MRPerfusionMiniAppBatchAction as perfusion
from avid.selectors.keyValueSelector import ActionTagSelector
from avid.common.AVIDUrlLocater import getToolConfigPath

@unittest.skipIf(getToolConfigPath('MRPerfusionMiniApp') is None, 'Tool MRPerfusionMiniApp is not installed on the system.')
class TestMRPerfusionMiniApp(unittest.TestCase):


    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "MRPerfusionMiniAppTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "MRPerfusionMiniAppTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_MRPerfusionMiniApp")
      
      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

              
    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_perf_descriptive_action(self):
      
      action = perfusion(ActionTagSelector("Signal"), model=perfusion.MODEL_DESCRIPTIVE, injectiontime = 0.1, actionTag = "TestPerf")
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)


if __name__ == "__main__":
    unittest.main()