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

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper

from avid.common import osChecker
from . import BatchActionBase
from .genericCLIAction import GenericCLIAction
from avid.linkers import CaseLinker
from avid.selectors import TypeSelector
from .simpleScheduler import SimpleScheduler
from avid.externals.plastimatch import parseCompareResult
from avid.externals.doseTool import saveSimpleDictAsResultXML

logger = logging.getLogger(__name__)


class PlmCompareAction(GenericCLIAction):
    """Class that wraps the single action for the tool plastimatch compare."""

    def __init__(self, refImage, inputImage,
                 actionTag="plmCompare", alwaysDo=False,
                 session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None, cli_connector=None):
        refImage = self._ensureSingleArtefact(refImage, "refImage")
        inputImage = self._ensureSingleArtefact(inputImage, "inputImage")

        GenericCLIAction.__init__(self, refImage=[refImage], inputImage=[inputImage], actionID="plastimatch",
                                  noOutputArgs=True,
                                  additionalArgs={'command': 'compare'},
                                  argPositions=['command', 'refImage', 'inputImage'],
                                  actionTag=actionTag, alwaysDo=alwaysDo, session=session,
                                  additionalActionProps=additionalActionProps, actionConfig=actionConfig,
                                  propInheritanceDict=propInheritanceDict, cli_connector=cli_connector,
                                  defaultoutputextension='xml')

    def _postProcessCLIExecution(self):
        resultPath = artefactHelper.getArtefactProperty(self.outputArtefacts[0], artefactProps.URL)
        osChecker.checkAndCreateDir(os.path.split(resultPath)[0])

        with open(self.logFilePath) as logfile:
            result = parseCompareResult(logfile.read())
            saveSimpleDictAsResultXML(result, resultPath)


class PlmCompareBatchAction(BatchActionBase):
    """Batch action for PlmCompareAction."""

    def __init__(self, refSelector, inputSelector, inputLinker=None, actionTag="plmCompare", session=None,
                 additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
        if inputLinker is None:
            inputLinker = CaseLinker()

        additionalInputSelectors = {"inputImage": inputSelector}
        linker = {"inputImage": inputLinker}

        BatchActionBase.__init__(self, actionTag=actionTag, actionClass=PlmCompareAction,
                                 primaryInputSelector=refSelector,
                                 primaryAlias="refImage", additionalInputSelectors=additionalInputSelectors,
                                 linker=linker, session=session,
                                 relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps=additionalActionProps,
                                 **singleActionParameters)
