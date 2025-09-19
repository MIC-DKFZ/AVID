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
from shutil import copyfile

import avid.common.artefact as artefactHelper
import avid.common.artefact.defaultProps as artefactProps
from avid.externals.matchPoint import FORMAT_VALUE_MATCHPOINT, getDeformationFieldPath
from avid.externals.plastimatch import FORMAT_VALUE_PLM_CXT
from avid.linkers import CaseLinker
from avid.selectors import TypeSelector
from avid.actions import BatchActionBase
from avid.actions.genericCLIAction import GenericCLIAction
from avid.common.cliConnector import default_artefact_url_extraction_delegate
from avid.actions.simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)


class PlmRTSSMapAction(GenericCLIAction):
    """Class that wraps the single action for the tool plastimatch convert in order to map DICOM RT SS via a
    registration. """

    @staticmethod
    def _plmRTSS_url_extraction_delegate(arg_name, arg_value):
        result = list()
        if arg_name == 'xf':
            for arg_artefact in arg_value:
                regPath = artefactHelper.getArtefactProperty(arg_artefact, artefactProps.URL)
                regFormat = artefactHelper.getArtefactProperty(arg_artefact, artefactProps.FORMAT)
                if regFormat == FORMAT_VALUE_MATCHPOINT:
                    fieldPath = getDeformationFieldPath(regPath)
                    if fieldPath is None:
                        raise RuntimeError(
                            "Cannot extract deformation field path from the given registration. Reg File: {}".format(
                                regPath))
                    else:
                        regPath = fieldPath
                result.append(regPath)
        elif arg_name == 'output-dicom':
            for arg_artefact in arg_value:
                output_path = artefactHelper.getArtefactProperty(arg_artefact, artefactProps.URL)
                result.append(os.path.splitext(output_path)[0])
        else:
            result = default_artefact_url_extraction_delegate(arg_name=arg_name, arg_value=arg_value)

        return result

    def __init__(self, rtss, registration, outputFormat=artefactProps.FORMAT_VALUE_DCM,
                 actionTag="plmRTSSMap", alwaysDo=False,
                 session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None, cli_connector=None):

        rtss = self._ensureSingleArtefact(rtss, "rtss")
        registration = self._ensureSingleArtefact(registration, "registration")
        self._outputFormat = outputFormat

        inputArgs = {'input': [rtss]}
        if registration is not None:
            inputArgs['xf'] = [registration]

        outputFlags = None
        if self._outputFormat == artefactProps.FORMAT_VALUE_DCM:
            outputFlags = ['output-dicom']
        elif self._outputFormat == FORMAT_VALUE_PLM_CXT:
            outputFlags = ['output-cxt']
        else:
            raise ValueError(
                'Output format is not supported by plmRTSSMap action. Choosen format: {}'.format(self._outputFormat))

        GenericCLIAction.__init__(self, **inputArgs, tool_id="plastimatch",
                                  outputFlags=outputFlags,
                                  argPositions=['command'],
                                  additionalArgsAsURL=['output-dicom', 'output-cxt'],
                                  inputArgsURLExtractionDelegate=self._plmRTSS_url_extraction_delegate,
                                  actionTag=actionTag, alwaysDo=alwaysDo, session=session,
                                  additionalActionProps=additionalActionProps, actionConfig=actionConfig,
                                  propInheritanceDict=propInheritanceDict, cli_connector=cli_connector,
                                  defaultoutputextension=self._getOutputExtension())

        additionalArgs = {'command': 'convert'}

        self.setAdditionalArguments(additionalArgs=additionalArgs)

    def _getOutputExtension(self):
        if self._outputFormat == artefactProps.FORMAT_VALUE_DCM:
            return 'dcm'
        elif self._outputFormat == FORMAT_VALUE_PLM_CXT:
            return 'cxt'
        else:
            raise ValueError(
                'Output format is not supported by plmRTSSMap action. Choosen format: {}'.format(self._outputFormat))

    def _postProcessCLIExecution(self):
        if self._outputFormat == artefactProps.FORMAT_VALUE_DCM:
            resultPath = artefactHelper.getArtefactProperty(self.outputArtefacts[0], artefactProps.URL)
            dicomDir = os.path.splitext(resultPath)[0]

            for file in os.listdir(dicomDir):
                copyfile(os.path.join(dicomDir, file), resultPath)
                break  # we assume that plastimatch outputs only on file (the warpped/mapped RT structure set) in the
                # result dir


class PlmRTSSMapBatchAction(BatchActionBase):
    """Batch action for PlmRTSSMapAction."""

    def __init__(self, rtssSelector, regSelector=None, regLinker=None, actionTag="plmRTSSMap", session=None,
                 additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
        if regLinker is None:
            regLinker = CaseLinker()

        additionalInputSelectors = {"registration": regSelector}
        linker = {"registration": regLinker}

        BatchActionBase.__init__(self, actionTag=actionTag, actionClass=PlmRTSSMapAction,
                                 primaryInputSelector=rtssSelector,
                                 primaryAlias="rtss", additionalInputSelectors=additionalInputSelectors,
                                 linker=linker, session=session,
                                 relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps=additionalActionProps,
                                 **singleActionParameters)
