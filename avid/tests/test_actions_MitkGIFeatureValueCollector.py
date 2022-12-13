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
import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper
from avid.actions.MitkGIFeatureValueCollector import MitkGIFeatureValueCollectorBatchAction as collector
from avid.selectors import CaseSelector
from avid.selectors.keyValueSelector import ActionTagSelector
from avid.splitter import KeyValueSplitter


class MitkGIFeatureValueCollector(unittest.TestCase):


    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "MitkGIFeatureValueCollectorTest")
      self.testSmallArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "MitkGIFeatureValueCollectorTest", "testlist_small.avid")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "MitkGIFeatureValueCollectorTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary","test_MitkGIFeatureValueCollector")
      self.tempRoot = os.path.join(os.path.split(__file__)[0],"temporary")

              
    def tearDown(self):
      try:
        shutil.rmtree(self.tempRoot)
      except:
        pass


    def readFile(self, filePath):
      result = None
      with open(filePath) as fileHandle:
        result = fileHandle.read()
        
      return result


    def test_simple_batch_action(self):
      session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testSmallArtefactFile)

      action = collector(ActionTagSelector('GIF'))
      token = action.do()
      self.assertEqual(token.isSuccess(), True)

      #refFile = os.path.join(self.testDataDir, "ref_simple_small_values.csv")
      #resultFile = artefactHelper.getArtefactProperty(action._actions[0].outputArtefacts[0], artefactProps.URL)
      #self.assertEqual(self.readFile(refFile), self.readFile(resultFile))


      action = collector(feature_selector=ActionTagSelector('GIF'),selected_features = ['Mean'], value_table = False,
                         column_key = artefactProps.OBJECTIVE)
      token = action.do()
      self.assertEqual(token.isSuccess(), True)


    def test_batch_action(self):
        session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

        action = collector(ActionTagSelector('GIF'), row_keys = [artefactProps.CASE, artefactProps.OBJECTIVE, artefactProps.TIMEPOINT])
        token = action.do()
        self.assertEqual(token.isSuccess(), True)

        #refFile = os.path.join(self.testDataDir, "ref_simple_small_values.csv")
        #resultFile = artefactHelper.getArtefactProperty(action._actions[0].outputArtefacts[0], artefactProps.URL)
        #self.assertEqual(self.readFile(refFile), self.readFile(resultFile))


        action = collector(feature_selector=ActionTagSelector('GIF'),selected_features = ['Mean'], value_table = False,
                           row_keys = [artefactProps.CASE, artefactProps.TIMEPOINT], column_key = artefactProps.OBJECTIVE)
        token = action.do()
        self.assertEqual(token.isSuccess(), True)

        action = collector(feature_selector=ActionTagSelector('GIF'), feature_splitter=KeyValueSplitter(artefactProps.OBJECTIVE),
                           selected_features = ['Mean'], value_table = False,
                           row_keys = [artefactProps.CASE], column_key = artefactProps.TIMEPOINT)
        token = action.do()
        self.assertEqual(token.isSuccess(), True)


if __name__ == "__main__":
    unittest.main()