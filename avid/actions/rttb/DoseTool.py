# SPDX-FileCopyrightText: 2024, German Cancer Research Center (DKFZ), Division of Medical Image Computing (MIC)
#
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# or find it in LICENSE.txt.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import re

import avid.common.artefact as artefactHelper
import avid.common.artefact.defaultProps as artefactProps
import avid.externals.virtuos as virtuos
from avid.linkers import CaseLinker
from avid.linkers.caseInstanceLinker import CaseInstanceLinker
from avid.selectors import TypeSelector
from avid.actions import BatchActionBase
from avid.actions.rttb.doseMap import _getArtefactLoadStyle
from avid.actions.genericCLIAction import GenericCLIAction
from avid.actions.simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)


class DoseToolAction(GenericCLIAction):
    """Class that wraps the single action for the tool RTTB DoseTool."""

    def __init__(self, inputDose, structSet, structName, computeDVH=True,
                 actionTag="DoseStat", alwaysDo=False, session=None,
                 additionalActionProps=None, actionConfig=None, propInheritanceDict=None, cli_connector=None):

        self._inputDose = self._ensureSingleArtefact(inputDose, "inputDose")
        self._structSet = self._ensureSingleArtefact(structSet, "structSet")
        self._structName = structName
        self._init_session(session)
        self._structName = structName
        self._computeDVH = computeDVH

        outputFlags = ['doseStatistics']
        if computeDVH:
            outputFlags.append('DVH')

        additionalArgs = {'structName': self._getStructPattern(self._structSet),
                          'doseLoadStyle': _getArtefactLoadStyle(self._inputDose),
                          'structLoadStyle': _getStructLoadStyle(self._structSet)}

        GenericCLIAction.__init__(self, structFile=[self._structSet], doseFile=[self._inputDose], tool_id="DoseTool",
                                  outputFlags=outputFlags,
                                  additionalArgs=additionalArgs,
                                  actionTag=actionTag, alwaysDo=alwaysDo, session=session,
                                  actionConfig=actionConfig,
                                  additionalActionProps=additionalActionProps,
                                  propInheritanceDict=propInheritanceDict, cli_connector=cli_connector,
                                  defaultoutputextension='xml')

    def _indicateOutputs(self):
        self._resultArtefact = self.generateArtefact(self._inputDose,
                                                     userDefinedProps={
                                                         artefactProps.TYPE: artefactProps.TYPE_VALUE_RESULT,
                                                         artefactProps.FORMAT: artefactProps.FORMAT_VALUE_RTTB_STATS_XML,
                                                         artefactProps.OBJECTIVE: self._structName},
                                                     url_user_defined_part=self.instanceName,
                                                     url_extension='xml')
        result = [self._resultArtefact]

        if self._computeDVH is True:
            name = self.instanceName
            name = name.replace("DoseTool", "CumDVH", 1)
            self._resultDVHArtefact = self.generateArtefact(self._inputDose,
                                                            userDefinedProps={
                                                                artefactProps.TYPE: artefactProps.TYPE_VALUE_RESULT,
                                                                artefactProps.FORMAT: artefactProps.FORMAT_VALUE_RTTB_CUM_DVH_XML,
                                                                artefactProps.OBJECTIVE: self._structName},
                                                            url_user_defined_part=name,
                                                            url_extension='xml')
            result.append(self._resultDVHArtefact)
        return result

    def _getStructPattern(self, structArtefact):
        aFormat = artefactHelper.getArtefactProperty(structArtefact, artefactProps.FORMAT)
        pattern = self._structName
        if not aFormat == artefactProps.FORMAT_VALUE_ITK:
            if self._session.hasStructurePattern(self._structName):
                pattern = self._session.structureDefinitions[self._structName]
            else:
                # we stay with the name, but be sure that it is a valid regex. because it
                # is expected by the doseTool
                pattern = re.escape(pattern)

        return pattern


def _getStructLoadStyle(structArtefact):
    """deduce the load style parameter for an artefact that should be input"""
    aPath = artefactHelper.getArtefactProperty(structArtefact, artefactProps.URL)
    aFormat = artefactHelper.getArtefactProperty(structArtefact, artefactProps.FORMAT)

    result = ""

    if aFormat == artefactProps.FORMAT_VALUE_ITK:
        result = aFormat
    elif aFormat == artefactProps.FORMAT_VALUE_DCM:
        result = "dicom"
    elif aFormat == artefactProps.FORMAT_VALUE_HELAX_DCM:
        result = "helax"
    elif aFormat == artefactProps.FORMAT_VALUE_VIRTUOS:
        result = "virtuos"
        ctxPath = virtuos.stripFileExtensions(aPath)
        ctxPath = ctxPath + os.extsep + "ctx"
        if not os.path.isfile(ctxPath):
            ctxPath = ctxPath + os.extsep + "gz"
            if not os.path.isfile(ctxPath):
                msg = "Cannot calculate dose statistic. Virtuos cube for use struct file not faund. Struct file: " + aPath
                logger.error(msg)
                raise RuntimeError(msg)

        result = result + ' "' + ctxPath + '"'
    else:
        logger.info("No load style known for artefact format: %s", aFormat)

    return result


def _dosetool_creation_delegate(structNames, **kwargs):
    actions = list()
    actionArgs = kwargs.copy()
    for name in structNames:
        actionArgs['structName'] = name
        actions.append(DoseToolAction(**actionArgs))
    return actions


class DoseStatBatchAction(BatchActionBase):
    """Base class for the DoseTool action."""

    def __init__(self, doseSelector, structSetSelector, structNames,
                 structLinker=None, actionTag="doseStat", session=None, additionalActionProps=None,
                 scheduler=SimpleScheduler(), **singleActionParameters):
        """
        :param structNames: List of the structures names for which a statistic should
            be generated. If none is passed all structures defined in current session's structure
            definitions.
        """

        if structLinker is None:
            structLinker = CaseLinker() + CaseInstanceLinker()

        additionalInputSelectors = {"structSet": structSetSelector}
        linker = {"structSet": structLinker}

        self._init_session(session)
        if structNames is None:
            structNames = list(self._session.structureDefinitions.keys())

        BatchActionBase.__init__(self, actionTag=actionTag, actionCreationDelegate=_dosetool_creation_delegate,
                                 primaryInputSelector=doseSelector, primaryAlias='inputDose',
                                 additionalInputSelectors=additionalInputSelectors, linker=linker,
                                 session=session, relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps=additionalActionProps,
                                 structNames=structNames, **singleActionParameters)
