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

import os
import logging
import subprocess

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper
import re

from avid.common import osChecker, AVIDUrlLocater
from avid.linkers import CaseLinker
from avid.linkers import FractionLinker
from avid.splitter import BaseSplitter, KeyValueSplitter

from . import BatchActionBase
from .genericCLIAction import GenericCLIAction
from avid.selectors import TypeSelector
from .simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)


class MitkResampleImageAction(GenericCLIAction):
    '''Class that wraps the single action for the tool MITKResampleImage.'''
    def __init__(self, images, additionalArgs= None, defaultoutputextension ='nrrd', actionTag="MitkResampleImage",
                 alwaysDo=False, session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None):
        GenericCLIAction.__init__(self, i=images, actionID="MitkResampleImage", outputFlags=['o'],
                                  additionalArgs=additionalArgs, illegalArgs= ['output', 'input'], actionTag= actionTag,
                                  alwaysDo=alwaysDo, session=session, additionalActionProps=additionalActionProps,
                                  actionConfig=actionConfig, propInheritanceDict=propInheritanceDict,
                                  defaultoutputextension=defaultoutputextension)


class MitkResampleImageBatchAction(BatchActionBase):
    '''Batch action for MitkResampleImage to produce XML results.'''

    def __init__(self, imageSelector,
                 actionTag="MITKResampleImage", session=None,
                 additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):

        BatchActionBase.__init__(self, actionTag=actionTag, actionClass=MitkResampleImageAction,
                                 primaryInputSelector=imageSelector,
                                 primaryAlias="images", additionalInputSelectors=None,
                                 linker=None, session=session,
                                 relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps=additionalActionProps,
                                 legacyOutput = False, **singleActionParameters)
