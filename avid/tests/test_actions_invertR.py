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

# workaround a pyCharm bug
from __future__ import absolute_import
import os
import shutil
import unittest

import avid.common.workflow as workflow
from avid.actions.invertR import invertRBatchAction as invertR
from avid.selectors.keyValueSelector import ActionTagSelector
from avid.common.AVIDUrlLocater import getToolConfigPath


@unittest.skipIf(getToolConfigPath('invertR') is None, 'Tool invertR not installed on the system.')
class TestInvertR(unittest.TestCase):

    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0], "data", "invertRTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0], "data", "invertRTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0], "temporary", "test_invertR")
      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_inversion_action(self):
        action = invertR(ActionTagSelector("Registration"), actionTag="TestReg")
        token = action.do()

        self.assertEqual(token.isSuccess(), True)

        token = action.do()
        self.assertEqual(token.isSkipped(), True)

    def test_simple_inversion_action_always_do(self):
        action = invertR(ActionTagSelector("Registration"), actionTag="TestReg", alwaysDo=True)
        token = action.do()

        self.assertEqual(token.isSuccess(), True)
        token = action.do()
        self.assertEqual(token.isSuccess(), True)

    def test_inversion_with_template_image_action(self):
        action = invertR(ActionTagSelector("Registration"), templateSelector=ActionTagSelector("Target"), actionTag="TestReg")
        token = action.do()
        self.assertEqual(token.isSuccess(), True)

if __name__ == "__main__":
    unittest.main()
