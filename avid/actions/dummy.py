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

import os
from builtins import str

import avid.common.artefact as artefactHelper
import avid.common.artefact.defaultProps as artefactProps
from avid.actions import SingleActionBase
from avid.actions.cliActionBase import CLIActionBase
from avid.common import AVIDUrlLocater, osChecker

from ..actions import BatchActionBase
from .simpleScheduler import SimpleScheduler


class DummySingleAction(SingleActionBase):

    def __init__(
        self,
        artefacts,
        actionTag,
        alwaysDo=False,
        session=None,
        additionalActionProps=None,
        propInheritanceDict=None,
    ):
        SingleActionBase.__init__(
            self,
            actionTag,
            alwaysDo,
            session,
            additionalActionProps=additionalActionProps,
            propInheritanceDict=propInheritanceDict,
        )
        self._artefacts = artefacts

        inputs = dict()
        for pos, a in enumerate(artefacts):
            inputs["i" + str(pos)] = [a]

        self._addInputArtefacts(**inputs)
        self.callCount_generateOutputs = 0

    def _generateName(self):
        name = "Dummy"
        return name

    def _indicateOutputs(self):
        return self._artefacts

    def _generateOutputs(self):
        self.callCount_generateOutputs = self.callCount_generateOutputs + 1
        pass


class DummyBatchAction(BatchActionBase):
    def __init__(
        self,
        artefactSelector,
        actionTag="Dummy",
        scheduler=SimpleScheduler(),
        session=None,
        additionalActionProps=None,
        **singleActionParameters,
    ):

        BatchActionBase.__init__(
            self,
            actionTag=actionTag,
            actionClass=DummySingleAction,
            primaryInputSelector=artefactSelector,
            primaryAlias="artefacts",
            session=session,
            scheduler=scheduler,
            additionalActionProps=additionalActionProps,
            **singleActionParameters,
        )


class DummyCLIAction(CLIActionBase):
    """Class that wraps the single action for the AVID dummy cli."""

    def __init__(
        self,
        input,
        actionTag="DummyCLI",
        will_fail=False,
        will_skip=False,
        alwaysDo=False,
        session=None,
        additionalActionProps=None,
        actionConfig=None,
    ):
        CLIActionBase.__init__(
            self,
            actionTag,
            alwaysDo,
            session,
            additionalActionProps,
            None,
            actionConfig=None,
        )

        self._addInputArtefacts(input=input)

        self._input = input
        self.will_fail = will_fail
        self.will_skip = will_skip

    def _generateName(self):
        name = (
            f"Dummy_{self.actionTag}_{artefactHelper.getArtefactProperty(self._input[0],artefactProps.ACTIONTAG)}"
            f"_#{artefactHelper.getArtefactProperty(self._input[0],artefactProps.TIMEPOINT)}"
        )

        return name

    def _indicateOutputs(self):
        if self.will_skip:
            self._resultArtefact = self._input[
                0
            ]  # by directly passing back the input as output indication it will allways force a skipping
        else:
            self._resultArtefact = self.generateArtefact(
                self._input[0],
                userDefinedProps={
                    artefactProps.TYPE: artefactProps.TYPE_VALUE_RESULT,
                    artefactProps.FORMAT: artefactProps.FORMAT_VALUE_CSV,
                },
                url_user_defined_part=self.instanceName,
                url_extension="txt",
            )
        return [self._resultArtefact]

    def _prepareCLIExecution(self):

        if self.will_fail:
            self._reportWarning("This is a test warning")
            return 'echo "Dummy action failed om purpose." >&2'

        resultPath = artefactHelper.getArtefactProperty(
            self._resultArtefact, artefactProps.URL
        )
        inputPath = artefactHelper.getArtefactProperty(
            self._input[0], artefactProps.URL
        )

        osChecker.checkAndCreateDir(os.path.split(resultPath)[0])

        content = f'echo "{inputPath} into {resultPath}" > {resultPath}'

        return content


class DummyCLIBatchAction(BatchActionBase):
    def __init__(
        self,
        artefacts,
        actionTag="DummyCLI",
        alwaysDo=False,
        scheduler=SimpleScheduler(),
        session=None,
    ):

        BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session=session)
        self._artefacts = artefacts

        BatchActionBase.__init__(
            self,
            actionTag=actionTag,
            actionClass=DummyCLIAction,
            primaryInputSelector=targetSelector,
            primaryAlias="targetImage",
            additionalInputSelectors=additionalInputSelectors,
            linker=linker,
            dependentLinker=dependentLinker,
            session=session,
            relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
            scheduler=scheduler,
            additionalActionProps=additionalActionProps,
            **singleActionParameters,
        )

    def _generateActions(self):
        actions = []
        for artefact in self._artefacts:
            action = DummyCLIAction(
                artefact, alwaysDo=self._alwaysDo, session=self._session
            )
            actions.append(action)

        return actions
