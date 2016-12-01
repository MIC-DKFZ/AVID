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

import os
import logging
import csv
import collections

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper
from avid.common import osChecker, AVIDUrlLocater

from . import BatchActionBase
from cliActionBase import CLIActionBase
from avid.selectors import TypeSelector
from simpleScheduler import SimpleScheduler
from avid.linkers import FractionLinker
from avid.selectors.keyValueSelector import FormatSelector
from avid.common.AVIDUrlLocater import getAVIDProjectRootPath
import avid.common.templateFileCustomizer as templateFileCustomizer

logger = logging.getLogger(__name__)

class ArimaAction(CLIActionBase):

  def __init__(self, doseStatsCollector, selectedStats=None, nPlannedFractions=25, rTemplateFile = os.path.join(getAVIDProjectRootPath(), "templates", "arima.R"), rowKey='Fractions',
               columnKey='Percentil', withHeaders=True, actionTag="Arima",
               alwaysDo=False, session=None, additionalActionProps=None, actionConfig = None, propInheritanceDict = dict()):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig = actionConfig, propInheritanceDict = propInheritanceDict)
    self._doseStatsCollector = doseStatsCollector

    self._nPlannedFractions = nPlannedFractions
    self._keys = selectedStats
    self._rTemplateFile = rTemplateFile
    self._rowKey = rowKey
    self._columnKey = columnKey
    self._resultArtefacts = dict()
    self._withHeaders = withHeaders

  def _generateName(self):
    name = "arima" +"_" + str(artefactHelper.getArtefactProperty(self._doseStatsCollector,artefactProps.DOSE_STAT))
    return name

  def _indicateOutputs(self):
    artefactRef = self._doseStatsCollector

    name = self._generateName()

    # Specify batch artefact
    self._batchArtefact = self.generateArtefact(artefactRef)
    self._batchArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_MISC
    self._batchArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_BAT

    path = artefactHelper.generateArtefactPath(self._session, self._batchArtefact)
    batName = name + "." + str(
      artefactHelper.getArtefactProperty(self._batchArtefact, artefactProps.ID)) + os.extsep + "bat"
    batName = os.path.join(path, batName)

    self._batchArtefact[artefactProps.URL] = batName

    # Specify config artefact
    self._configArtefact = self.generateArtefact(self._batchArtefact)
    self._configArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_CONFIG
    self._configArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_R

    path = artefactHelper.generateArtefactPath(self._session, self._configArtefact)
    resName = name + "." + str(
      artefactHelper.getArtefactProperty(self._configArtefact, artefactProps.ID)) + os.extsep + "r"
    resName = os.path.join(path, resName)

    self._configArtefact[artefactProps.URL] = resName

    # Specify result artefact
    self._resultArtefact = self.generateArtefact(self._batchArtefact)
    self._resultArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._resultArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_CSV

    path = artefactHelper.generateArtefactPath(self._session, self._resultArtefact)
    resName = name + "." + str(
      artefactHelper.getArtefactProperty(self._resultArtefact, artefactProps.ID)) + os.extsep + "csv"
    resName = os.path.join(path, resName)

    self._resultArtefact[artefactProps.URL] = resName

    return [self._batchArtefact, self._configArtefact, self._resultArtefact]

  def _generateConfigFile(self, configPath):
      """load the .R template file and insert the missing values"""
      RFilename = artefactHelper.getArtefactProperty(self._configArtefact, artefactProps.URL)
      resultCSVFilename = artefactHelper.getArtefactProperty(self._resultArtefact, artefactProps.URL)
      csvDataFilename = artefactHelper.getArtefactProperty(self._doseStatsCollector, artefactProps.URL)

      resultCSVFilename = resultCSVFilename.replace("\\", "/")
      csvDataFilename = csvDataFilename.replace("\\", "/")

      #workingDirectory = os.path.dirname(configPath)
      #workingDirectory = workingDirectory.replace("\\", "/")

      replacingDict = {"@CSV_FILE@": csvDataFilename, "@ENDTIME@": self._nPlannedFractions, \
                       "@ROW_KEY@": self._rowKey, "@COLUMN_KEY@": self._columnKey, \
                       "@RESULT_CSV_FILE@": resultCSVFilename}
      templateFileCustomizer.writeFileCustomized(self._rTemplateFile, RFilename, replacingDict)

  def _prepareCLIExecution(self):
    batPath = artefactHelper.getArtefactProperty(self._batchArtefact, artefactProps.URL)
    configPath = artefactHelper.getArtefactProperty(self._configArtefact, artefactProps.URL)
    resultPath = artefactHelper.getArtefactProperty(self._resultArtefact, artefactProps.URL)

    osChecker.checkAndCreateDir(os.path.split(batPath)[0])
    osChecker.checkAndCreateDir(os.path.split(configPath)[0])
    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])

    self._generateConfigFile(configPath)

    execURL = AVIDUrlLocater.getExecutableURL(self._session, "Rscript", self._actionConfig)

    content = '"' + execURL + '"' + ' "' + configPath + '"'

    with open(batPath, "w") as outputFile:
      outputFile.write(content)
      outputFile.close()

    return batPath


class ArimaBatchAction(BatchActionBase):
  '''Batch class for the dose collection actions.'''

  def __init__(self, doseStatsSelector, planSelector = None, planLinker = FractionLinker(useClosestPast=True),
               actionTag="arima", alwaysDo=False,
               session=None, additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._doseStatsCollector = doseStatsSelector.getSelection(self._session.inData)

    if planSelector is not None:
      self._plans = planSelector.getSelection(self._session.inData)
    self._planLinker = planLinker
    self._singleActionParameters = singleActionParameters

  def _generateActions(self):
    # filter only type result. Other artefact types are not interesting
    resultCSVSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT) + FormatSelector(artefactProps.FORMAT_VALUE_CSV)
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)
    inputs = self.ensureValidArtefacts(self._doseStatsCollector, resultCSVSelector, "input stats")

    plans = self.ensureValidArtefacts(self._plans, resultSelector, "plans")

    global logger
    if len(inputs) == 0:
      logger.debug("Input selection contains no usable artefacts (type = result).")

    actions = list()
    for input in inputs:
      #linkedPlans = self._planLinker.getLinkedSelection(0, inputs, plans)

      if len(plans) > 0:
        #lPlan = linkedPlans[0]
        nPlannedFractions = artefactHelper.getArtefactProperty(plans[0], artefactProps.PLANNED_FRACTIONS)
        action = ArimaAction(input, nPlannedFractions=nPlannedFractions,
                             actionTag=self._actionTag, alwaysDo=self._alwaysDo,
                             session=self._session,
                             additionalActionProps=self._additionalActionProps,
                             **self._singleActionParameters)

        actions.append(action)
      else:
        logger.info(
          "No plan selected, no fraction number information available. ).")

    return actions
