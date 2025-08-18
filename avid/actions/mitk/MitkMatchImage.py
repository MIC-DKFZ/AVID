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
from json import dumps as jsonDumps

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper
from avid.linkers import CaseLinker

from avid.actions import BatchActionBase
from avid.actions.genericCLIAction import GenericCLIAction
from avid.selectors import TypeSelector
from avid.actions.simpleScheduler import SimpleScheduler
from avid.externals.matchPoint import FORMAT_VALUE_MATCHPOINT

logger = logging.getLogger(__name__)

class MitkMatchImageAction(GenericCLIAction):
    '''Class that wraps the single action for the tool MitkMatchImage.'''

    @staticmethod
    def _indicate_outputs(actionInstance, **allActionArgs):
        userDefinedProps = {artefactProps.TYPE: artefactProps.TYPE_VALUE_RESULT}

        artefactRef = actionInstance._targetImage[0]
        if actionInstance._targetIsArtefactReference is False:
            if actionInstance._movingImage is None:
                logger.error("Moving image is None and can't be used as Reference")
                raise
            else:
                artefactRef = actionInstance._movingImage[0]

        resultArtefact = actionInstance.generateArtefact(artefactRef,
                                                         userDefinedProps={artefactProps.TYPE:artefactProps.TYPE_VALUE_RESULT,
                                                                           artefactProps.FORMAT: FORMAT_VALUE_MATCHPOINT},
                                                         url_user_defined_part=actionInstance._generateName(),
                                                         url_extension='mapr')
        return [resultArtefact]

    @staticmethod
    def _defaultNameCallable(actionInstance, **allActionArgs):
        name = "reg_"+artefactHelper.getArtefactShortName(actionInstance._movingImage[0])

        name += "_to_"+artefactHelper.getArtefactShortName(actionInstance._targetImage[0])

        return name

    def __init__(self, targetImage, movingImage, algorithm, algorithmParameters = None,
                 targetIsArtefactReference = True, actionTag="MitkMatchImage",
                 alwaysDo=False, session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None,
                 generateNameCallable=None, cli_connector=None):

        self._targetImage = [self._ensureSingleArtefact(targetImage, "targetImage")]
        self._movingImage = [self._ensureSingleArtefact(movingImage, "movingImage")]
        self._algorithm = algorithm
        self._targetIsArtefactReference = targetIsArtefactReference

        additionalArgs = {'a':self._algorithm}
        self._algorithmParameters = algorithmParameters
        if not self._algorithmParameters is None:
            additionalArgs['parameters'] = jsonDumps(self._algorithmParameters).replace('"', '\\"')

        if generateNameCallable is None:
            generateNameCallable = self._defaultNameCallable

        GenericCLIAction.__init__(self, t=self._targetImage, m=self._movingImage, actionID="MitkMatchImage", outputFlags=['o'],
                                  additionalArgs=additionalArgs, illegalArgs= ['output', 'moving', 'target'],
                                  defaultoutputextension='mapr', actionTag= actionTag, alwaysDo=alwaysDo, session=session,
                                  indicateCallable=self._indicate_outputs, generateNameCallable=generateNameCallable,
                                  additionalActionProps=additionalActionProps,
                                  actionConfig=actionConfig, propInheritanceDict=propInheritanceDict, cli_connector=cli_connector)


class MitkMatchImageBatchAction(BatchActionBase):
    '''Batch action for MitkMatchImage that produces a stitched 4D image.
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

    def __init__(self, targetSelector, movingSelector, movingLinker = None,
                 actionTag="MitkMatchImage", session=None,
                 additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):

        if movingLinker is None:
            movingLinker = CaseLinker()

        additionalInputSelectors = {"movingImage": movingSelector}
        linker = {"movingImage": movingLinker}

        BatchActionBase.__init__(self, actionTag= actionTag, actionClass=MitkMatchImageAction,
                                 primaryInputSelector= targetSelector,
                                 primaryAlias="targetImage", additionalInputSelectors = additionalInputSelectors,
                                 linker = linker, session= session,
                                 relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps = additionalActionProps, **singleActionParameters)

