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
from builtins import range

import avid.common.artefact.defaultProps as artefactProps
from avid.externals.matchPoint import FORMAT_VALUE_MATCHPOINT
from avid.linkers import CaseLinker
from avid.selectors import TypeSelector
from . import BatchActionBase
from .genericCLIAction import GenericCLIAction
from .simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)


class RegVarToolAction(GenericCLIAction):
    """Class that wraps the single action for the tool regVarTool."""

    def __init__(self, registration, instanceNr, algorithmDLL, regParameters=None, templateImage=None,
                 actionTag="regVarTool",
                 alwaysDo=False, session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None, cli_connector=None):

        registration = self._ensureSingleArtefact(registration, "registration")
        templateImage = self._ensureSingleArtefact(templateImage, "templateImage")

        inputArgs = {'r': [registration]}
        if templateImage is not None:
            inputArgs['i'] = [templateImage]

        additionalArgs = {'a': algorithmDLL}
        if regParameters is not None:
            argVal = list()
            for pKey in regParameters:
                argVal.append(pKey)
                argVal.append(regParameters[pKey])
            additionalArgs['p'] = argVal

        if additionalActionProps is None:
            additionalActionProps = dict()
        additionalActionProps[artefactProps.FORMAT] = FORMAT_VALUE_MATCHPOINT

        GenericCLIAction.__init__(self, **inputArgs, actionID="RegVarTool",
                                  additionalArgs=additionalArgs,
                                  outputFlags=['o'],
                                  actionTag=actionTag, alwaysDo=alwaysDo, session=session,
                                  additionalActionProps=additionalActionProps, actionConfig=actionConfig,
                                  propInheritanceDict=propInheritanceDict, cli_connector=cli_connector,
                                  defaultoutputextension='mapr')

        if self._caseInstance is not None and not instanceNr == self._caseInstance:
            logger.warning(
                "Case instance conflict between input artefacts (%s) and instance that should be defined by action (%s).",
                self._caseInstance, instanceNr)
        self._instanceNr = instanceNr
        self._caseInstance = instanceNr

    def _generateName(self):
        return super()._generateName() + '_Var#{}'.format(self._instanceNr)


class RegVarToolBatchAction(BatchActionBase):
    """Action for batch processing of the RegVarTool."""

    @staticmethod
    def _regvar_creation_delegate(instanceNr, **kwargs):
        actions = list()
        actionArgs = kwargs.copy()
        for pos in range(0, instanceNr):
            actionArgs['instanceNr'] = pos
            actions.append(RegVarToolAction(**actionArgs))
        return actions

    def __init__(self, regSelector, variationCount, templateSelector=None,
                 templateLinker=None,
                 actionTag="regVarTool",
                 session=None, additionalActionProps=None, scheduler=SimpleScheduler(),
                 **singleActionParameters):

        if templateLinker is None:
            templateLinker = CaseLinker()

        additionalInputSelectors = {"templateImage": templateSelector}
        linker = {"templateImage": templateLinker}

        BatchActionBase.__init__(self, actionTag=actionTag, actionCreationDelegate=self._regvar_creation_delegate,
                                 primaryInputSelector=regSelector, primaryAlias="registration",
                                 additionalInputSelectors=additionalInputSelectors, linker=linker,
                                 session=session, relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps=additionalActionProps,
                                 instanceNr=variationCount, **singleActionParameters)
