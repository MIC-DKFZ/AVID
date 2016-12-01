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
from avid.actions.pdc import pdcBatchAction as pdc
from avid.selectors.keyValueSelector import ActionTagSelector
from avid.common.artefact import Artefact
from avid.common.artefact import generateArtefactEntry
import avid.common.artefact.defaultProps as defaultProps
from avid.common.AVIDUrlLocater import getToolConfigPath

class TestPDC(unittest.TestCase):


    def setUp(self):
      
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "pdcTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "pdcTest", "testlist.avid")
            
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_pdc")

      self.batPath = os.path.join(os.path.split(__file__)[0],"data", "pdcTest", "PDC_template.bat")
         
      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True)
      
      pdcDataPath = os.path.join(os.path.dirname(getToolConfigPath('pdc++')),'Resources', 'TestData','data','2000_TEST_B')
      plan = generateArtefactEntry('case1', None, 0, 'Plan', defaultProps.TYPE_VALUE_RESULT, defaultProps.FORMAT_VALUE_VIRTUOS, os.path.join(pdcDataPath, '2000_TEST_B108.pln'))
      self.session.inData.append(plan)
      ct = generateArtefactEntry('case1', None, 0, 'BPLCT', defaultProps.TYPE_VALUE_RESULT, defaultProps.FORMAT_VALUE_VIRTUOS, os.path.join(pdcDataPath, '2000_TEST_B000.ctx.gz'))
      self.session.inData.append(ct)
      structurset = generateArtefactEntry('case1', None, 0, 'Struct', defaultProps.TYPE_VALUE_RESULT, defaultProps.FORMAT_VALUE_VIRTUOS, os.path.join(pdcDataPath, '2000_TEST_B000.vdx'))
      self.session.inData.append(structurset)

              
    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_pdc_action(self):
      
      action = pdc(ActionTagSelector("BPLCT"), ActionTagSelector("Plan"), ActionTagSelector("Struct"), actionTag = "TestPDC", executionBat = self.batPath)     
      token = action.do()
      self.assertEqual(token.isSuccess(), True)


if __name__ == "__main__":
    unittest.main()