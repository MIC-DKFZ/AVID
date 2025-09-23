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
from avid.actions import BatchActionBase
from avid.actions.cliActionBase import CLIActionBase
from avid.actions.simpleScheduler import SimpleScheduler
from avid.common import osChecker
from avid.externals.matchPoint import ensureMAPRegistrationArtefact
from avid.linkers import CaseLinker, FractionLinker, LinkerBase
from avid.selectors import TypeSelector

logger = logging.getLogger(__name__)


class mapRAction(CLIActionBase):
    """Class that wraps the single action for the tool mapR."""
    def __init__(self, inputImage, registration=None, templateImage=None,
                 interpolator="linear", outputExt="nrrd", paddingValue=None,
                 actionTag="mapR", inputIsReference=True, alwaysDo=False,
                 session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None, cli_connector=None):
        CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, tool_id="mapR",
                               actionConfig=actionConfig, propInheritanceDict=propInheritanceDict, cli_connector=cli_connector)
        self._addInputArtefacts(inputImage=inputImage, registration=registration, templateImage=templateImage)

        self._inputImage = self._ensureSingleArtefact(inputImage, "inputImage")
        self._registration = self._ensureSingleArtefact(registration, "regstration")
        self._templateImage = self._ensureSingleArtefact(templateImage, "templateImage")
        self._interpolator = interpolator
        self._outputExt = outputExt
        self._paddingValue = paddingValue
        self._inputIsReference = inputIsReference

    def _generateName(self):
        name = "map_" + artefactHelper.getArtefactShortName(self._inputImage)

        if self._registration is not None:
            name += "_reg_" + artefactHelper.getArtefactShortName(self._registration)
        else:
            name += "_identity"

        if self._templateImage is not None:
            name += "_to_" + artefactHelper.getArtefactShortName(self._templateImage)

        return name

    def _hasDICOMinput(self):
        return self._outputExt.lower() == "dcm" or self._outputExt.lower() == "ima"

    def _indicateOutputs(self):
        userDefinedProps = {artefactProps.TYPE: artefactProps.TYPE_VALUE_RESULT}
        if self._hasDICOMinput():
            userDefinedProps[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_DCM

        artefactRef = self._inputImage
        if self._inputIsReference is False:
            if self._templateImage is None:
                logger.error("template image is None and can't be used as Reference")
                raise
            else:
                artefactRef = self._templateImage

        resultArtefact = self.generateArtefact(artefactRef,
                                               userDefinedProps=userDefinedProps,
                                               url_user_defined_part=self.instanceName,
                                               url_extension=self._outputExt)
        return [resultArtefact]

    def _prepareCLIExecution(self):

        resultPath = artefactHelper.getArtefactProperty(self.outputArtefacts[0], artefactProps.URL)
        inputPath = artefactHelper.getArtefactProperty(self._inputImage, artefactProps.URL)
        templatePath = artefactHelper.getArtefactProperty(self._templateImage, artefactProps.URL)
        registrationPath = artefactHelper.getArtefactProperty(self._registration, artefactProps.URL)

        result = ensureMAPRegistrationArtefact(self._registration, self.generateArtefact(self._inputImage),
                                               self._session)
        if result[0]:
            if result[1] is None:
                logger.error(
                    "Mapping will fail. Given registration is not MatchPoint compatible and cannot be converted.")
            else:
                registrationPath = artefactHelper.getArtefactProperty(result[1], artefactProps.URL)
                logger.debug(
                    "Converted/Wrapped given registration artefact to be MatchPoint compatible. Wrapped artefact path: " + registrationPath)

        osChecker.checkAndCreateDir(os.path.split(resultPath)[0])

        execURL = self._cli_connector.get_executable_url(self._session, self._actionID, self._actionConfig)

        content = '"' + execURL + '"' + ' "' + inputPath + '"'
        if registrationPath is not None:
            content += ' "' + registrationPath + '"'

        if templatePath is not None:
            content += ' -t "' + templatePath + '"'

        content += ' -o "' + resultPath + '"'
        content += ' -i ' + self._interpolator + ' --handleMappingFailure'

        if self._paddingValue is not None:
            content += ' -p %s' % self._paddingValue

        if self._hasDICOMinput():
            content += ' --seriesReader dicom'

        return content


class mapRBatchAction(BatchActionBase):
    '''Standard batch action class for mapR actions.'''

    def __init__(self, inputSelector, registrationSelector=None, templateSelector=None,
                 regLinker=None, templateLinker=None,
                 actionTag="mapR", session=None, additionalActionProps=None,
                 scheduler=SimpleScheduler(), templateRegLinker=None,
                 **singleActionParameters):
        """@param inputSelector Selector for the artefacts that should be mapped.
        @param registrationSelector Selector for the artefacts that specify the registration. If no registrations are
        specified, an identity transform will be assumed.
        @param templateSelector Selector for the reference geometry that should be used to map into it. If None is
        specified, the geometry of the input will be used.
        @param regLinker Linker to select the registration that should be used on an input. Default is FractionLinker.
        @param templateLinker Linker to select the reference geometry that should be used to map an input. Default is CaseLinker.
        @param templateRegLinker Linker to select which regs (resulting from the regLinker should be used regarding
        the template that will be used. Default is LinkerBase (so every link registration will be used with every linked
        template."""

        if regLinker is None:
            regLinker = FractionLinker()
        if templateLinker is None:
            templateLinker = CaseLinker()
        if templateRegLinker is None:
            templateRegLinker = LinkerBase()

        additionalInputSelectors = {"registration": registrationSelector, "templateImage": templateSelector}
        linker = {"registration": regLinker, "templateImage": templateLinker}
        dependentLinker = {"registration": ("templateImage", templateRegLinker)}

        BatchActionBase.__init__(self, actionTag=actionTag, actionClass=mapRAction, primaryInputSelector=inputSelector,
                                 primaryAlias="inputImage", additionalInputSelectors=additionalInputSelectors,
                                 linker=linker, dependentLinker=dependentLinker, session=session,
                                 relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps=additionalActionProps,
                                 **singleActionParameters)
