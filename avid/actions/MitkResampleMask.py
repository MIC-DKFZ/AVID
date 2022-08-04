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

from . import BatchActionBase
from .genericCLIAction import GenericCLIAction
from avid.selectors import TypeSelector
from .simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)

class MitkResampleMaskAction(GenericCLIAction):
    '''Class that wraps the single action for the tool MitkResampleMask.'''

    def __init__(self, images, additionalArgs= None, defaultoutputextension ='nrrd', actionTag="MitkResampleMask",
                 alwaysDo=False, session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None, cli_connector=None):
        GenericCLIAction.__init__(self, i=images, actionID="MitkResampleMask", outputFlags=['o'],
                                  additionalArgs=additionalArgs, illegalArgs= ['output', 'input'], actionTag= actionTag,
                                  alwaysDo=alwaysDo, session=session, additionalActionProps=additionalActionProps,
                                  actionConfig=actionConfig, propInheritanceDict=propInheritanceDict, cli_connector=cli_connector,
                                  defaultoutputextension=defaultoutputextension)


class MitkResampleMaskBatchAction(BatchActionBase):
    '''Batch action for MitkResampleMask.'''

    def __init__(self, imageSelector,
                 actionTag="MitkResampleMask", session=None,
                 additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
        BatchActionBase.__init__(self, actionTag=actionTag, actionClass=MitkResampleMaskAction,
                                 primaryInputSelector=imageSelector,
                                 primaryAlias="images", additionalInputSelectors=None,
                                 linker=None, session=session,
                                 relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps=additionalActionProps,
                                 **singleActionParameters)
