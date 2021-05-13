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
from avid.actions.pointSetConversion import PointSetConversionBatchAction as psConversion
from avid.externals.fcsv import FORMAT_VALUE_SLICER_POINTSET
from avid.externals.matchPoint import FORMAT_VALUE_MATCHPOINT_POINTSET
from avid.selectors.keyValueSelector import ActionTagSelector
import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper

class TestPointSetConversion(unittest.TestCase):


    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "pointSetConversionTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "pointSetConversionTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_pointSetConversion")
      
      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

              
    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass


    def test_to_simpleMatchPoint(self):
      
      action = psConversion(ActionTagSelector("SourcePS"), targetformat=FORMAT_VALUE_MATCHPOINT_POINTSET,
                            actionTag="TestToMatchPoint", alwaysDo=False)
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)

      refFilePath = os.path.join(self.testDataDir, "refMatchPoint"+os.extsep+"txt")
      resultFilePath = artefactHelper.getArtefactProperty(action._actions[0].outputArtefacts[0],
                                                      artefactProps.URL)
      with open(refFilePath) as refFile:
          with open(resultFilePath) as resultFile:
              self.assertEqual(refFile.read(), resultFile.read())

      resultFilePath = artefactHelper.getArtefactProperty(action._actions[1].outputArtefacts[0],
                                                      artefactProps.URL)
      with open(refFilePath) as refFile:
          with open(resultFilePath) as resultFile:
              self.assertEqual(refFile.read(), resultFile.read())

      token = action.do()
      self.assertEqual(token.isSkipped(), True)

    def test_to_fcsv(self):
        action = psConversion(ActionTagSelector("SourcePS"), targetformat=FORMAT_VALUE_SLICER_POINTSET,
                              actionTag="TestToFCSV", alwaysDo=False)
        token = action.do()

        self.assertEqual(token.isSuccess(), True)

        refFilePath = os.path.join(self.testDataDir, "refMatchPoint" + os.extsep + "fcsv")
        resultFilePath = artefactHelper.getArtefactProperty(action._actions[0].outputArtefacts[0],
                                                        artefactProps.URL)
        with open(refFilePath) as refFile:
            with open(resultFilePath) as resultFile:
                self.assertEqual(refFile.read(), resultFile.read())

        refFilePath = os.path.join(self.testDataDir, "ref3dslicer" + os.extsep + "fcsv")
        resultFilePath = artefactHelper.getArtefactProperty(action._actions[1].outputArtefacts[0],
                                                        artefactProps.URL)
        with open(refFilePath) as refFile:
            with open(resultFilePath) as resultFile:
                self.assertEqual(refFile.read(), resultFile.read())

        token = action.do()
        self.assertEqual(token.isSkipped(), True)

if __name__ == "__main__":
    unittest.main()