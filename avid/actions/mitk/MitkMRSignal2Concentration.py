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

import avid.common.artefact.defaultProps as artefactProps
from avid.selectors import TypeSelector
from avid.actions import BatchActionBase
from avid.actions.genericCLIAction import GenericCLIAction
from avid.actions.simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)


class MitkMRSignal2ConcentrationAction(GenericCLIAction):
    """Class that wrapps the single action for the tool MitkMRSignal2Concentration."""
    CONVERSION_T1_ABSOLUTE = "t1-absolute"
    CONVERSION_T1_RELATIVE = "t1-relative"
    CONVERSION_T1_FLASH = "t1-flash"
    CONVERSION_T2 = "t2"

    def __init__(self, signal, conversiontype=CONVERSION_T1_ABSOLUTE, k=1, recoveryTime=None,
                 relaxivity=None, relaxationTime=None, te=None, actionTag="MitkMRSignal2Concentration", alwaysDo=False,
                 session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None, cli_connector=None):

        signal = self._ensureSingleArtefact(signal, "signal")

        self._conversiontype = conversiontype
        self._k = k
        self._recoveryTime = recoveryTime
        self._relaxivity = relaxivity
        self._relaxationTime = relaxationTime
        self._te = te

        if te is None and conversiontype == self.CONVERSION_T2:
            raise RuntimeError("Cannot convert T2 without parameter TE set.")
        if conversiontype == self.CONVERSION_T1_FLASH and (
                recoveryTime is None or relaxationTime is None or relaxivity is None):
            raise RuntimeError(
                "Cannot convert T1 flash without parameter recoveryTime, relaxationTime and relaxivity set.")

        additionalArgs = {self._conversiontype: None}
        if self._conversiontype == self.CONVERSION_T1_ABSOLUTE or self._conversiontype == self.CONVERSION_T1_RELATIVE:
            additionalArgs['k'] = self._k
        elif self._conversiontype == self.CONVERSION_T1_FLASH:
            additionalArgs['k'] = self._k
            additionalArgs['TE'] = self._te
        elif self._conversiontype == self.CONVERSION_T2:
            additionalArgs['relaxivity'] = self._relaxivity
            additionalArgs['recovery-time'] = self._recoveryTime
            additionalArgs['relaxation-time'] = self._relaxationTime

        if additionalActionProps is None:
            additionalActionProps = dict()
        additionalActionProps[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_ITK

        GenericCLIAction.__init__(self, i=[signal], tool_id="MitkMRSignal2Concentration",
                                  outputFlags=['o'],
                                  additionalArgs=additionalArgs,
                                  actionTag=actionTag, alwaysDo=alwaysDo, session=session,
                                  additionalActionProps=additionalActionProps, actionConfig=actionConfig,
                                  propInheritanceDict=propInheritanceDict, cli_connector=cli_connector,
                                  defaultoutputextension='nrrd')


class MitkMRSignal2ConcentrationBatchAction(BatchActionBase):
    """Batch action for MitkMRSignal2Concentration."""

    CONVERSION_T1_ABSOLUTE = MitkMRSignal2ConcentrationAction.CONVERSION_T1_ABSOLUTE
    CONVERSION_T1_RELATIVE = MitkMRSignal2ConcentrationAction.CONVERSION_T1_RELATIVE
    CONVERSION_T1_FLASH = MitkMRSignal2ConcentrationAction.CONVERSION_T1_FLASH
    CONVERSION_T2 = MitkMRSignal2ConcentrationAction.CONVERSION_T2

    def __init__(self, signalSelector, actionTag='MitkMRSignal2Concentration', session=None,
                 additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
        BatchActionBase.__init__(self, actionTag=actionTag, actionClass=MitkMRSignal2ConcentrationAction,
                                 primaryInputSelector=signalSelector,
                                 primaryAlias="signal", session=session,
                                 relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps=additionalActionProps,
                                 **singleActionParameters)
