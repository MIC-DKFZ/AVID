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
from avid.actions.MitkFileConverter import MitkFileConverterBatchAction as convert
from avid.selectors.keyValueSelector import ActionTagSelector

from avid.common.AVIDUrlLocater import getExecutableURL

@unittest.skipIf(getExecutableURL(None, 'MitkFileConverter') is None, 'Tool MitkFileConverter not installed on the system.')
class TestMitkFileConverter(unittest.TestCase):

    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "mapRTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "mapRTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_MitkFileConvert")

      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)


    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_convert_action(self):

      action = convert(inputSelector=ActionTagSelector("Moving"), actionTag = "TestConvert")
      token = action.do()

      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSkipped(), True)

      action = convert(ActionTagSelector("Moving"), defaultoutputextension='nii',
                      actionTag="TestConvert2")
      token = action.do()

      self.assertEqual(token.isSuccess(), True)

    def test_simple_convert_action_alwaysdo(self):

      action = convert(inputSelector=ActionTagSelector("Moving"), actionTag = "TestConvertAlwaysDo", alwaysDo=True)
      token = action.do()

      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSuccess(), True)


if __name__ == "__main__":
    unittest.main()
