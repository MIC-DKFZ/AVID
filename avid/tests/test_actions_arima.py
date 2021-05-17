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

import unittest, os, shutil
import avid.common.workflow as workflow
from avid.actions.legacy.arima import ArimaBatchAction as arima
from avid.selectors.keyValueSelector import ActionTagSelector
from avid.selectors.keyValueSelector import DoseStatSelector
from avid.common.AVIDUrlLocater import getToolConfigPath

@unittest.skipIf(getToolConfigPath('RScript') is None, 'Tool RScript not installed on the system.')
class TestArima(unittest.TestCase):
  def setUp(self):
    self.testDataDir = os.path.join(os.path.split(__file__)[0], "data", "arimaTest")
    self.testArtefactFile = os.path.join(os.path.split(__file__)[0], "data", "arimaTest", "testlist.avid")
    self.sessionDir = os.path.join(os.path.split(__file__)[0], "temporary_test_arima")

    self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True,
                                        bootstrapArtefacts=self.testArtefactFile)

  def tearDown(self):
    try:
      shutil.rmtree(self.sessionDir)
    except:
      pass

  def test_simple_arima_action(self):

    action = arima(ActionTagSelector("collector")+DoseStatSelector("maximum"), planSelector=ActionTagSelector("plan"), selectedStats="maximum", actionTag="SimpleArima")
    token = action.do()
    self.assertEqual(token.isSuccess(), True)
    token = action.do()
    self.assertEqual(token.isSkipped(), True)


if __name__ == "__main__":
  unittest.main()
