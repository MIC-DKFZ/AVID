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

import logging, os
import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper
from avid.common import osChecker, AVIDUrlLocater
from cliActionBase import CLIActionBase
from . import BatchActionBase
from avid.selectors import TypeSelector
from avid.selectors.keyValueSelector import FormatSelector
from simpleScheduler import SimpleScheduler
import avid.common.templateFileCustomizer as templateFileCustomizer

logger = logging.getLogger(__name__)

class doseProcessVisualizerAction(CLIActionBase):
    '''Class that produces a diagram of the dose with R.'''
    def __init__(self, doseStatVariations, doseStatBaseline, doseStatAdditional, rTemplateFile, diagramTitle="", xAxisName="", yAxisName="", actionTag = "DoseProcessVisualizer", alwaysDo = False,
               session = None, additionalActionProps = None, rScriptExe = "Rscript.exe"):
        CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps)

        self._doseStatVariations = doseStatVariations[0]
        self._doseStatBaseline = doseStatBaseline[0]
        if doseStatAdditional is not None:
            self._doseStatAdditional = doseStatAdditional[0]
        else:
            self._doseStatAdditional = None
        self._rTemplateFile = rTemplateFile
        self._diagramTitle = diagramTitle
        self._xAxisName = xAxisName
        self._yAxisName = yAxisName

        self.rScriptExe = rScriptExe

        self._addInputArtefacts(doseStatVariations = self._doseStatVariations, doseStatBaseline = self._doseStatBaseline, doseStatAdditional = self._doseStatAdditional)


    def _generateName(self):
        name = "vis_"+str(self._diagramTitle)+"_"+str(artefactHelper.getArtefactProperty(self._doseStatVariations,artefactProps.ACTIONTAG))\
                +"_" + str(artefactHelper.getArtefactProperty(self._doseStatBaseline,artefactProps.ACTIONTAG))

        if self._doseStatAdditional is not None:
          name += "_"+str(artefactHelper.getArtefactProperty(self._doseStatAdditional,artefactProps.ACTIONTAG))

        return name

    def _indicateOutputs(self):
        artefactRef = self._doseStatVariations

        name = self._generateName()

        #Specify batch artefact
        self._batchArtefact = self.generateArtefact(artefactRef)
        self._batchArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_MISC
        self._batchArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_BAT
        self._batchArtefact["diagram_type"] = self._diagramTitle

        path = artefactHelper.generateArtefactPath(self._session, self._batchArtefact)
        batName = name + "." + str(artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.ID)) + os.extsep + "bat"
        batName = os.path.join(path, batName)

        self._batchArtefact[artefactProps.URL] = batName

        #Specify config artefact
        self._configArtefact = self.generateArtefact(self._batchArtefact)
        self._configArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_CONFIG
        self._configArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_R
        self._configArtefact["diagram_type"] = self._diagramTitle

        path = artefactHelper.generateArtefactPath(self._session, self._configArtefact)
        resName = name + "." + str(artefactHelper.getArtefactProperty(self._configArtefact,artefactProps.ID)) + os.extsep + "r"
        resName = os.path.join(path, resName)

        self._configArtefact[artefactProps.URL] = resName

        #Specify result artefact
        self._resultArtefact = self.generateArtefact(self._batchArtefact)
        self._resultArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
        self._resultArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_PNG
        self._resultArtefact["diagram_type"] = self._diagramTitle

        path = artefactHelper.generateArtefactPath(self._session, self._resultArtefact)
        resName = name + "." + str(artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.ID)) + os.extsep + "png"
        resName = os.path.join(path, resName)

        self._resultArtefact[artefactProps.URL] = resName

        return [self._batchArtefact, self._configArtefact, self._resultArtefact]


    def _getRelativeFilename(self, targetFilename, sourceFilename):
        pathList = [targetFilename, sourceFilename]
        common_prefix = os.path.commonprefix(pathList)
        if common_prefix in targetFilename:
            countDirectoriesCommonPrefix = common_prefix.count('\\')
            countDirectoriesTarget = targetFilename.count('\\')
            dotDotPrefix = str()
            for i in range(0,countDirectoriesTarget-countDirectoriesCommonPrefix):
                dotDotPrefix += "..\\"
            return dotDotPrefix+os.path.relpath(targetFilename, common_prefix)
        else:
            return targetFilename

    def _generateConfigFile(self, configPath):
        """load the .R template file and insert the missing values"""
        RFilename = artefactHelper.getArtefactProperty(self._configArtefact,artefactProps.URL)
        PNGFilename = artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.URL)
        csvDataFilename = artefactHelper.getArtefactProperty(self._doseStatVariations,artefactProps.URL)
        csvBaselineFilename = artefactHelper.getArtefactProperty(self._doseStatBaseline,artefactProps.URL)
        if self._doseStatAdditional is not None:
            csvCompareFilename = artefactHelper.getArtefactProperty(self._doseStatAdditional,artefactProps.URL)
        else :
            csvCompareFilename = ""

        relativePNGFilename = self._getRelativeFilename(PNGFilename, RFilename)
        relativePNGFilename = relativePNGFilename.replace("\\", "/")
        csvDataFilename = csvDataFilename.replace("\\", "/")
        csvBaselineFilename = csvBaselineFilename.replace("\\", "/")
        csvCompareFilename = csvCompareFilename.replace("\\", "/")

        workingDirectory = os.path.dirname(configPath)
        workingDirectory = workingDirectory.replace("\\", "/")

        replacingDict = {"@WORKING_DIRECTORY@" : workingDirectory, "@CSVDATA_FILE@" : csvDataFilename, \
                         "@CSVBASELINE_FILE@" : csvBaselineFilename, "@CSVADDITIONALDATA_FILE@" : csvCompareFilename, \
                         "@PNG_FILE@": relativePNGFilename, "@TITLE_NAME@" : self._diagramTitle, "@XAXIS_NAME@":self._xAxisName, "@YAXIS_NAME@" : self._yAxisName }
        templateFileCustomizer.writeFileCustomized(self._rTemplateFile, RFilename, replacingDict)

    def _prepareCLIExecution(self):
        batPath = artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.URL)
        configPath = artefactHelper.getArtefactProperty(self._configArtefact,artefactProps.URL)
        resultPath = artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.URL)

        osChecker.checkAndCreateDir(os.path.split(batPath)[0])
        osChecker.checkAndCreateDir(os.path.split(configPath)[0])
        osChecker.checkAndCreateDir(os.path.split(resultPath)[0])

        self._generateConfigFile(configPath)

        execURL = AVIDUrlLocater.getExecutableURL(self._session, "Rscript", self.rScriptExe)

        content = '"' + execURL + '"' + ' "' + configPath + '"'

        with open(batPath, "w") as outputFile:
          outputFile.write(content)
          outputFile.close()

        return batPath

class doseProcessVisualizerBatchAction(BatchActionBase):
    def __init__(self,  doseStatVariationsSelector, doseStatBaselineSelector, doseStatAdditionalSelector,
               rTemplateFile, diagramTitle = "",xAxisName="", yAxisName="",
               actionTag = "DoseProcessVisualizer", alwaysDo = False,
               session = None, additionalActionProps = None, rScriptExe = "Rscript.exe", scheduler = SimpleScheduler()):
        BatchActionBase.__init__(self,actionTag, alwaysDo, scheduler, session, additionalActionProps)

        self._doseStatVariations = doseStatVariationsSelector.getSelection(self._session.inData)
        self._doseStatBaseline = doseStatBaselineSelector.getSelection(self._session.inData)
        if doseStatAdditionalSelector is not None:
            self._doseStatAdditional = doseStatAdditionalSelector.getSelection(self._session.inData)
        else :
            self._doseStatAdditional = None

        self._rTemplateFile = rTemplateFile
        self._diagramTitle = diagramTitle
        self._xAxisName = xAxisName
        self._yAxisName = yAxisName
        self._rScriptExe = rScriptExe


    def _generateActions(self):
        #filter only type result. Other artefact types are not interesting
        resultCsvSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT) + FormatSelector(artefactProps.FORMAT_VALUE_CSV)
        doseStatVariations = self.ensureRelevantArtefacts(self._doseStatVariations, resultCsvSelector, "doseStat variations")
        doseStatBaseline = self.ensureRelevantArtefacts(self._doseStatBaseline, resultCsvSelector, "doseStat baseline")
        if self._doseStatAdditional is not None:
            doseStatAdditional = self.ensureRelevantArtefacts(self._doseStatAdditional, resultCsvSelector, "doseStat additional")
        else:
            doseStatAdditional = None

        global logger

        if len(doseStatVariations) == 0 or len(doseStatBaseline) == 0:
            logger.debug("Input selection contains no usable artefacts (type = result and format = csv).")

        actions = list()

        action = doseProcessVisualizerAction(doseStatVariations, doseStatBaseline, doseStatAdditional, self._rTemplateFile, self._diagramTitle,
                   self._xAxisName, self._yAxisName, self._actionTag,
                   self._alwaysDo, self._session, self._additionalActionProps, self._rScriptExe)
        actions.append(action)

        return actions