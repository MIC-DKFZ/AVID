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
import avid.common.artefact as artefactHelper

from avid.linkers import CaseLinker, LinkerBase
from avid.linkers import FractionLinker

from avid.actions import BatchActionBase
from avid.actions.genericCLIAction import GenericCLIAction
from avid.selectors import TypeSelector
from avid.actions.simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)

INTERPOLATOR_NN = 0
INTERPOLATOR_LINEAR = 1
STITCH_STRATEGY_MEAN = 0
STITCH_STRATEGY_BORDER_DISTANCE = 1

class MitkMapImageAction(GenericCLIAction):
    '''Class that wrapps the single action for the tool MitkMapImage.'''

    @staticmethod
    def _indicate_outputs(actionInstance, **allActionArgs):
        userDefinedProps = {artefactProps.TYPE: artefactProps.TYPE_VALUE_RESULT}

        artefactRef = actionInstance._inputImage[0]
        if actionInstance._inputIsArtefactReference is False:
            if actionInstance._templateImage is None:
                logger.error("template image is None and can't be used as Reference")
                raise
            else:
                artefactRef = actionInstance._templateImage

        resultArtefact = actionInstance.generateArtefact(artefactRef,
                                                         userDefinedProps=userDefinedProps,
                                                         url_user_defined_part=actionInstance.instanceName,
                                                         url_extension=actionInstance._outputExt)
        return [resultArtefact]

    @staticmethod
    def _defaultNameCallable(actionInstance, **allActionArgs):
        name = "map_" + artefactHelper.getArtefactShortName(actionInstance._inputImage[0])

        if actionInstance._registration is not None:
            name += "_reg_" + artefactHelper.getArtefactShortName(actionInstance._registration)
        else:
            name += "_identity"

        if actionInstance._templateImage is not None:
            name += "_to_" + artefactHelper.getArtefactShortName(actionInstance._templateImage)

        return name

    def __init__(self, inputImage, registration = None, templateImage=None, actionTag="MitkMapImage",
                 paddingValue = None, interpolator=None, supersamplingFactor=None, outputExt="nrrd", inputIsArtefactReference=True,
                 alwaysDo=False, session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None,
                 generateNameCallable=None, cli_connector=None):

        self._inputImage = [self._ensureSingleArtefact(inputImage, "inputImage")]
        self._registration = self._ensureSingleArtefact(registration, "regstration")
        self._templateImage = self._ensureSingleArtefact(templateImage, "templateImage")
        self._interpolator = interpolator
        self._outputExt = outputExt
        self._paddingValue = paddingValue
        self._supersamplingFactor = supersamplingFactor
        self._inputIsArtefactReference = inputIsArtefactReference

        additionalArgs = dict()
        if interpolator:
            additionalArgs['interpolator'] = str(interpolator)
        if paddingValue:
            additionalArgs['p'] = str(paddingValue)
        if supersamplingFactor:
            additionalArgs['s'] = supersamplingFactor

        inputs = {'i':self._inputImage}
        if self._registration is not None:
            inputs['r'] = [self._registration]
        if self._templateImage is not None:
            inputs['t'] = [self._templateImage]

        if generateNameCallable is None:
            generateNameCallable = self._defaultNameCallable

        GenericCLIAction.__init__(self, **inputs, actionID="MitkMapImage", outputFlags=['o'],
                                  additionalArgs=additionalArgs, illegalArgs= ['output', 'input', 'template', 'registration'],
                                  actionTag= actionTag, alwaysDo=alwaysDo, session=session, indicateCallable=self._indicate_outputs,
                                  generateNameCallable=generateNameCallable, additionalActionProps=additionalActionProps,
                                  actionConfig=actionConfig, propInheritanceDict=propInheritanceDict, cli_connector=cli_connector)


class MitkMapImageBatchAction(BatchActionBase):
    '''Batch action for MitkMapImage that maps images by a given registration into a given reference geometry.
        @param imageSpltter specify the splitter that should be used to seperate the images into "input selection" that
        should be stitched. Default is a single split which leads to the same behavior like a simple 1 image mapping.
        @param regSplitter specify the splitter that should be used to seperate the registrations into "input selection"
        that should be used for stitching. Default is a single split which leads to the same behavior like a simple 1
        image mapping.
        @param imageSorter specifies if and how an image selection should be sorted. This is relevant if registrations
        are also selected because the stitching assumes that images and registrations have the same order to identify
        the corresponding registration for each image.
        @param regSorter specifies if and how an registration selection should be sorted. This is relevant if registrations
        are also selected because the stitching assumes that images and registrations have the same order to identify
        the corresponding registration for each image.'''

    def __init__(self, inputSelector, registrationSelector=None, templateSelector=None,
                 regLinker=None, templateLinker=None, templateRegLinker=None,
                 actionTag="MitkMapImage", session=None,
                 additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):

        if regLinker is None:
            regLinker = FractionLinker()
        if templateLinker is None:
            templateLinker = CaseLinker()
        if templateRegLinker is None:
            templateRegLinker = LinkerBase()

        additionalInputSelectors = {"registration": registrationSelector, "templateImage": templateSelector}
        linker = {"registration": regLinker, "templateImage": templateLinker}
        dependentLinker = {"registration": ("templateImage", templateRegLinker)}

        BatchActionBase.__init__(self, actionTag=actionTag, actionClass=MitkMapImageAction, primaryInputSelector=inputSelector,
                                 primaryAlias="inputImage", additionalInputSelectors=additionalInputSelectors,
                                 linker=linker, dependentLinker=dependentLinker, session=session,
                                 relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps=additionalActionProps,
                                 **singleActionParameters)
