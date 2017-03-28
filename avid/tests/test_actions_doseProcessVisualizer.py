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
from avid.actions.doseProcessVisualizer import doseProcessVisualizerBatchAction as doseProcessVisualizer
from avid.selectors import ActionTagSelector
from avid.common.AVIDUrlLocater import getAVIDProjectRootPath
import avid.common.templateFileCustomizer as templateFileCustomizer
from avid.common.AVIDUrlLocater import getToolConfigPath

@unittest.skipIf(getToolConfigPath('RScript') is None, 'Tool RScript not installed on the system.')
class TestDoseProcessVisualizer(unittest.TestCase):


    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "doseProcessVisualizerTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "doseProcessVisualizerTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_doseProcessVisualizer")
      self.tempRoot = os.path.join(os.path.split(__file__)[0],"temporary")
      self.rTemplateFile = os.path.join(getAVIDProjectRootPath(),"templates", "diagramCSVSource.R")
      self.rTemplateAdditionalFile = os.path.join(getAVIDProjectRootPath(),"templates", "deltaDiagramWithQuantilAndAdditionalDataCSVSource.R")
      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)


    def tearDown(self):
        try:
            shutil.rmtree(self.tempRoot)
        except :
            pass

    def readFile(self, filePath):
      result = None
      with open(filePath) as fileHandle:
        result = fileHandle.read()

      return result


    def test_simple_batch_action(self):

      action = doseProcessVisualizer(ActionTagSelector("collector"), ActionTagSelector("plannedCollector"), None, self.rTemplateFile)
      token = action.do()

      refFile = os.path.join(self.testDataDir, "ref_vis_DoseStatsCollector_DoseStatsPlannedCollector.r")
      refCustomizedFile = os.path.join(self.tempRoot, "test_doseProcessVisualizer", "ref_vis_DoseStatsCollector_DoseStatsPlannedCollector.r")

      configFile = artefactHelper.getArtefactProperty(action._actions[0]._configArtefact, artefactProps.URL)
      batchFile = artefactHelper.getArtefactProperty(action._actions[0]._batchArtefact, artefactProps.URL)
      resultFile = artefactHelper.getArtefactProperty(action._actions[0]._resultArtefact, artefactProps.URL)

      workingDirectory = os.path.dirname(configFile)
      csvDataFilename = os.path.join(self.testDataDir, "doseStatCollector_maximum.csv")
      csvBaselineFilename = os.path.join(self.testDataDir, "doseStatPlannedCollectorWithInterpolation_maximum.csv")

      workingDirectory = workingDirectory.replace("\\","/")
      csvDataFilename = csvDataFilename.replace("\\","/")
      csvBaselineFilename = csvBaselineFilename.replace("\\","/")

      replacingDict = {"@WORKING_DIRECTORY@" : workingDirectory, "@CSVDATA_FILE@" : csvDataFilename, \
                         "@CSVBASELINE_FILE@" : csvBaselineFilename, "@PNG_FILE@" : os.path.basename(resultFile) }
      templateFileCustomizer.writeFileCustomized(refFile, refCustomizedFile, replacingDict)

      self.assertEqual(token.isSuccess(), True)
      self.assertEqual(self.readFile(refCustomizedFile), self.readFile(configFile))
      self.assertEqual(os.path.isfile(resultFile), True)
      self.assertEqual(os.path.isfile(batchFile), True)


    def test_batch_action_with_additional_data(self):

      action = doseProcessVisualizer(ActionTagSelector("collector"), ActionTagSelector("plannedCollector"),  ActionTagSelector("additionalCollector"), self.rTemplateAdditionalFile)
      token = action.do()

      refFile = os.path.join(self.testDataDir, "ref_vis_DoseStatsCollector_DoseStatsPlannedCollector_DoseStatsAdditonalCollector.r")
      refCustomizedFile = os.path.join(self.tempRoot, "test_doseProcessVisualizer", "ref_vis_DoseStatsCollector_DoseStatsPlannedCollector_DoseStatsAdditonalCollector.r")
      configFile = artefactHelper.getArtefactProperty(action._actions[0]._configArtefact, artefactProps.URL)
      batchFile = artefactHelper.getArtefactProperty(action._actions[0]._batchArtefact, artefactProps.URL)
      resultFile = artefactHelper.getArtefactProperty(action._actions[0]._resultArtefact, artefactProps.URL)

      workingDirectory = os.path.dirname(configFile)
      csvDataFilename = os.path.join(self.testDataDir, "doseStatCollector_maximum.csv")
      csvBaselineFilename = os.path.join(self.testDataDir, "doseStatPlannedCollectorWithInterpolation_maximum.csv")
      csvAdditionalFilename = os.path.join(self.testDataDir, "doseStatAdditionalCollectorWithInterpolation_maximum.csv")

      workingDirectory = workingDirectory.replace("\\","/")
      csvDataFilename = csvDataFilename.replace("\\","/")
      csvBaselineFilename = csvBaselineFilename.replace("\\","/")
      csvAdditionalFilename = csvAdditionalFilename.replace("\\","/")

      replacingDict = {"@WORKING_DIRECTORY@" : workingDirectory, "@CSVDATA_FILE@" : csvDataFilename, \
                         "@CSVBASELINE_FILE@" : csvBaselineFilename, "@PNG_FILE@" : os.path.basename(resultFile), "@CSVADDITIONAL_FILE@" : csvAdditionalFilename }
      templateFileCustomizer.writeFileCustomized(refFile, refCustomizedFile, replacingDict)

      self.assertEqual(token.isSuccess(), True)
      self.assertEqual(self.readFile(refCustomizedFile), self.readFile(configFile))
      self.assertEqual(os.path.isfile(resultFile), True)
      self.assertEqual(os.path.isfile(batchFile), True)


if __name__ == "__main__":
    unittest.main()