# AVID
# Automated workflow system for cohort analysis in radiology and radiation therapy
#
# Copyright (c) German Cancer Research Center,
# Software development for Integrated Diagnostic and Therapy (SIDT).
# All rights reserved.
#
# This software is distributed WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.
#
# See LICENSE.txt or http://www.dkfz.de/en/sidt/index.html for details.

import logging

import avid.common.artefact.defaultProps as artefactProps
from avid.linkers import CaseLinker
from avid.linkers import FractionLinker

from . import BatchActionBase
from .genericCLIAction import GenericCLIAction
from avid.selectors import TypeSelector
from .simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)

class MitkMatchImageMiniAppAction(GenericCLIAction):
    '''Class that wraps the single action for the tool MitkMatchImageMiniApp.'''

    def __init__(self, targetImage, movingImage, algorithm, algorithmParameters = None,
                 targetIsArtefactReference = True, actionTag="MitkMatchImageMiniApp",
                 paddingValue = None, stitchStrategy=None, interpolator=None, alwaysDo=False,
                 session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None, cli_connector=None):

        self._targetImage = [self._ensureSingleArtefact(targetImage, "targetImage")]
        self._movingImage = [self._ensureSingleArtefact(movingImage, "movingImage")]
        self._algorithm = algorithm

        additionalArgs = {'a':self._algorithm}
        self._algorithmParameters = algorithmParameters
        if not self._algorithmParameters is None:
            content = ''
            for key, value in self._algorithmParameters.items():
                content += ' "' + key + '=' + value + '"'
            additionalArgs['parameters'] = str(content)

        GenericCLIAction.__init__(self, t=self._targetImage, m=self._movingImage, actionID="MitkMatchImageMiniApp", outputFlags=['o'],
                                  additionalArgs=additionalArgs, illegalArgs= ['output', 'moving', 'target'],
                                  defaultoutputextension='mapr', actionTag= actionTag, alwaysDo=alwaysDo, session=session, additionalActionProps=additionalActionProps,
                                  actionConfig=actionConfig, propInheritanceDict=propInheritanceDict, cli_connector=cli_connector)


class MitkMatchImageMiniAppBatchAction(BatchActionBase):
    '''Batch action for MitkMatchImageMiniApp that produces a stitched 4D image.
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
                 actionTag="MitkMatchImageMiniApp", session=None,
                 additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):

        if movingLinker is None:
            movingLinker = CaseLinker()

        additionalInputSelectors = {"movingImage": movingSelector}
        linker = {"movingImage": movingLinker}

        BatchActionBase.__init__(self, actionTag= actionTag, actionClass=MitkMatchImageMiniAppAction,
                                 primaryInputSelector= targetSelector,
                                 primaryAlias="targetImage", additionalInputSelectors = additionalInputSelectors,
                                 linker = linker, session= session,
                                 relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps = additionalActionProps, **singleActionParameters)

