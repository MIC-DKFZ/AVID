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
from avid.actions.plmRTSSMap import PlmRTSSMapBatchAction as plmRTTSMap
from avid.common.artefact.defaultProps import FORMAT_VALUE_DCM
from avid.externals.plastimatch import FORMAT_VALUE_PLM_CXT
from avid.selectors.keyValueSelector import ActionTagSelector
from avid.common.AVIDUrlLocater import getToolConfigPath

@unittest.skipIf(getToolConfigPath('Plastimatch') is None, 'Tool Plastimatch not installed on the system.')
class TestPlmRTSSMap(unittest.TestCase):

    def setUp(self):
      self.testRTSS = os.path.join(os.path.split(__file__)[0],"data", "voxelizerTest", "rtss.dcm")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_plmRTSSMap")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "voxelizerTest", "testlist.avid")

      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"),
                                          expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_action(self):
      
      action = plmRTTSMap(ActionTagSelector('Struct'), outputFormat = FORMAT_VALUE_DCM,
                          actionTag = "TestPlmRTSSMap")
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSkipped(), True)


    def test_action_cxt(self):
        action = plmRTTSMap(ActionTagSelector('Struct'), outputFormat=FORMAT_VALUE_PLM_CXT,
                            actionTag="TestPlmRTSSMap")
        token = action.do()

        self.assertEqual(token.isSuccess(), True)

    #TODO ad test that checks mapping with reg
    #def test_action_with_reg(self):

if __name__ == "__main__":
    unittest.main()