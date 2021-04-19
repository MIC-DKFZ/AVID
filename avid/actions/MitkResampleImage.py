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
from .cliActionBase import CLIActionBase
from avid.selectors import TypeSelector
from .simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)

class MitkResampleImageAction(CLIActionBase):
    '''Class that wraps the single action for the tool MITKResampleImage.'''

    def __init__(self, images, cliArgs= None, actionTag="MitkResampleImage", alwaysDo=False,
                 session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None):
        CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps,
                               actionID="MitkCLGlobalImageFeatures", actionConfig=actionConfig,
                               propInheritanceDict=propInheritanceDict)

        self._addInputArtefacts(images=images)
        self._images = self._ensureSingleArtefact(images, "images")

        self._cliArgs = dict()
        if cliArgs is not None:
            illegalArgs = ["i", "image", "o", "output"]
            for arg in cliArgs:
                if arg not in illegalArgs:
                    self._cliArgs[arg] = cliArgs[arg]
                else:
                    logger.warning('Ignored illegal argument "{}". It will be set by action'.format(arg))

    def _generateName(self):
        name = "res_{}".format(artefactHelper.getArtefactShortName(self._images))
        return name

    def _indicateOutputs(self):
        # Specify result artefact
        self._resultArtefact = self.generateArtefact(self._images,
                                                     userDefinedProps={artefactProps.TYPE: artefactProps.TYPE_VALUE_RESULT,
                                                                       artefactProps.FORMAT: artefactProps.FORMAT_VALUE_ITK},
                                                     urlHumanPrefix=self.instanceName, urlExtension='nrrd')
        return [self._resultArtefact]

    def _prepareCLIExecution(self):

        resultPath = artefactHelper.getArtefactProperty(self._resultArtefact, artefactProps.URL)
        imagePath = artefactHelper.getArtefactProperty(self._images, artefactProps.URL)

        osChecker.checkAndCreateDir(os.path.split(resultPath)[0])

        try:
            execURL = AVIDUrlLocater.getExecutableURL(self._session, self._actionID, self._actionConfig)

            content = '"{}" -i "{}" -o "{}"'.format(execURL, imagePath, resultPath)
            for arg in self._cliArgs:
                content += ' -{}'.format(arg)
                if self._cliArgs[arg] is not None:
                    content += ' {}'.format(self._cliArgs[arg])
        except:
            logger.error("Error for getExecutable.")
            raise

        return content


class MitkResampleImageBatchAction(BatchActionBase):
    '''Batch action for MITKCLGlobalImageFeatures to produce XML results.'''

    def __init__(self, imageSelector,
                 actionTag="MITKResampleImage", alwaysDo=False, session=None,
                 additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):

        BatchActionBase.__init__(self, actionTag=actionTag, actionClass=MitkResampleImageAction,
                                 primaryInputSelector=imageSelector,
                                 primaryAlias="images", additionalInputSelectors=None,
                                 linker=None, session=session,
                                 relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps=additionalActionProps,
                                 legacyOutput = False, **singleActionParameters)
