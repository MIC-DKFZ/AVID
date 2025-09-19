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

import avid.common.artefact as artefactHelper
import avid.common.artefact.defaultProps as artefactProps
from avid.common import osChecker
from avid.externals.doseTool import saveSimpleDictAsResultXML
from avid.externals.plastimatch import parseDiceResult
from avid.linkers import CaseLinker
from avid.selectors import TypeSelector
from avid.actions import BatchActionBase
from avid.actions.genericCLIAction import GenericCLIAction
from avid.actions.simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)


class PlmDiceAction(GenericCLIAction):
    """Class that wraps the single action for the tool plastimatch dice."""

    def __init__(self, refImage, inputImage,
                 actionTag="plmDice", alwaysDo=False,
                 session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None, cli_connector=None):
        refImage = self._ensureSingleArtefact(refImage, "refImage")
        inputImage = self._ensureSingleArtefact(inputImage, "inputImage")

        GenericCLIAction.__init__(self, refImage=[refImage], inputImage=[inputImage], tool_id="plastimatch",
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

        with open(self._last_log_file_path) as logFile:
            result = parseDiceResult(logFile.read())
            saveSimpleDictAsResultXML(result, resultPath)


class PlmDiceBatchAction(BatchActionBase):
    """Batch action for PlmDiceAction."""

    def __init__(self, refSelector, inputSelector, inputLinker=None, actionTag="plmDice", session=None,
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
