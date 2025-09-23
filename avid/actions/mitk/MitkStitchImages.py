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
import subprocess

import avid.common.artefact as artefactHelper
import avid.common.artefact.defaultProps as artefactProps
from avid.actions import BatchActionBase
from avid.actions.genericCLIAction import GenericCLIAction
from avid.actions.simpleScheduler import SimpleScheduler
from avid.common import AVIDUrlLocater, osChecker
from avid.linkers import CaseLinker, FractionLinker
from avid.selectors import TypeSelector
from avid.sorter import BaseSorter, KeyValueSorter
from avid.splitter import BaseSplitter, KeyValueSplitter

logger = logging.getLogger(__name__)

INTERPOLATOR_NN = 0
INTERPOLATOR_LINEAR = 1
STITCH_STRATEGY_MEAN = 0
STITCH_STRATEGY_BORDER_DISTANCE = 1

class MitkStitchImagesAction(GenericCLIAction):
    '''Class that wrapps the single action for the tool MitkStitchImages.'''

    def __init__(self, images, template, registrations = None, actionTag="MitkStitchImages",
                 paddingValue = None, stitchStrategy=None, interpolator=None, alwaysDo=False,
                 session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None, cli_connector=None):

        self._template = [self._ensureSingleArtefact(template, "template")]
        self._registrations = registrations
        if registrations is None:
            self._registrations = [None]
        self._paddingValue = paddingValue
        self._stitchStrategy = stitchStrategy
        self._interpolator = interpolator

        additionalArgs = dict()
        if interpolator:
            additionalArgs['interpolator'] = str(interpolator)
        if paddingValue:
            additionalArgs['p'] = str(paddingValue)
        if stitchStrategy:
            additionalArgs['s'] = str(stitchStrategy)

        GenericCLIAction.__init__(self, i=images, t=self._template, r=self._registrations, tool_id="MitkStitchImages", outputFlags=['o'],
                                  additionalArgs=additionalArgs, illegalArgs= ['output', 'input'], actionTag= actionTag,
                                  alwaysDo=alwaysDo, session=session, additionalActionProps=additionalActionProps,
                                  actionConfig=actionConfig, propInheritanceDict=propInheritanceDict, cli_connector=cli_connector)


class MitkStitchImagesBatchAction(BatchActionBase):
    '''Batch action for MitkStitchImages that produces a stitched 4D image.
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

    def __init__(self, imagesSelector, templateSelector, regsSelector = None, templateLinker = None, regLinker=None,
                 templateRegLinker=None, imageSplitter = None, regSplitter = None, imageSorter = None, regSorter = None,
                 actionTag="MitkStitchImages", session=None,
                 additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):

        if templateLinker is None:
            templateLinker = CaseLinker()
        if regLinker is None:
            regLinker = FractionLinker()
        if templateRegLinker is None:
            templateRegLinker = CaseLinker()

        additionalInputSelectors = {"template": templateSelector, "registrations": regsSelector}
        linker = {"template": templateLinker, "registrations": regLinker}
        dependentLinker = {"registrations": ("template", templateRegLinker)}

        sorter = None
        if imageSorter is not None or regSorter is not None:
            sorter = {}
            if imageSorter is not None:
                sorter[BatchActionBase.PRIMARY_INPUT_KEY] = imageSorter
            if regSorter is not None:
                sorter['registrations'] = regSorter

        splitter = None
        if imageSplitter is not None or regSplitter is not None:
            splitter = {}
            if imageSplitter is not None:
                splitter[BatchActionBase.PRIMARY_INPUT_KEY] = imageSplitter
            if regSplitter is not None:
                splitter['registrations'] = regSplitter

        BatchActionBase.__init__(self, actionTag=actionTag, actionClass=MitkStitchImagesAction,
                                 primaryInputSelector=imagesSelector,
                                 primaryAlias="images", additionalInputSelectors = additionalInputSelectors,
                                 linker = linker, dependentLinker=dependentLinker, splitter=splitter, sorter=sorter,
                                 session=session, relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps=additionalActionProps,
                                 **singleActionParameters)
