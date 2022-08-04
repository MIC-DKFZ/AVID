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

import logging
import os

import avid.common.artefact as artefactHelper
import avid.common.artefact.defaultProps as artefactProps
from avid.common import osChecker
from avid.externals.doseTool import saveSimpleDictAsResultXML
from avid.externals.plastimatch import parseDiceResult
from avid.linkers import CaseLinker
from avid.selectors import TypeSelector
from . import BatchActionBase
from .genericCLIAction import GenericCLIAction
from .simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)


class PlmDiceAction(GenericCLIAction):
    """Class that wraps the single action for the tool plastimatch dice."""

    def __init__(self, refImage, inputImage,
                 actionTag="plmDice", alwaysDo=False,
                 session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None, cli_connector=None):
        refImage = self._ensureSingleArtefact(refImage, "refImage")
        inputImage = self._ensureSingleArtefact(inputImage, "inputImage")

        GenericCLIAction.__init__(self, refImage=[refImage], inputImage=[inputImage], actionID="plastimatch",
                                  noOutputArgs=True,
                                  additionalArgs={'command': 'dice', 'all': None},
                                  argPositions=['command', 'refImage', 'inputImage'],
                                  actionTag=actionTag, alwaysDo=alwaysDo, session=session,
                                  additionalActionProps=additionalActionProps, actionConfig=actionConfig,
                                  propInheritanceDict=propInheritanceDict, cli_connector=cli_connector,
                                  defaultoutputextension='xml')

    def _postProcessCLIExecution(self):
        resultPath = artefactHelper.getArtefactProperty(self.outputArtefacts[0], artefactProps.URL)
        osChecker.checkAndCreateDir(os.path.split(resultPath)[0])

        with open(self._logFilePath) as logFile:
            result = parseDiceResult(logFile.read())
            saveSimpleDictAsResultXML(result, resultPath)


class PlmDiceBatchAction(BatchActionBase):
    """Batch action for PlmDiceAction."""

    def __init__(self, refSelector, inputSelector, inputLinker=None, actionTag="plmCompare", session=None,
                 additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
        if inputLinker is None:
            inputLinker = CaseLinker()

        additionalInputSelectors = {"inputImage": inputSelector}
        linker = {"inputImage": inputLinker}

        BatchActionBase.__init__(self, actionTag=actionTag, actionClass=PlmDiceAction,
                                 primaryInputSelector=refSelector,
                                 primaryAlias="refImage", additionalInputSelectors=additionalInputSelectors,
                                 linker=linker, session=session,
                                 relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps=additionalActionProps,
                                 **singleActionParameters)
