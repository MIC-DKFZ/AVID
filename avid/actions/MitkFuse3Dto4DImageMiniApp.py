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
from avid.sorter import BaseSorter, KeyValueSorter
from avid.splitter import BaseSplitter, KeyValueSplitter

from . import BatchActionBase
from .cliActionBase import CLIActionBase
from avid.selectors import TypeSelector
from .simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)

FORMAT_VALUE_MITK_GIF_XML = 'mitk_cl_gif_xml'

class MitkFuse3Dto4DImageMiniAppAction(CLIActionBase):
    '''Class that wrapps the single action for the tool MITK CLGlobalImageFeatures.'''

    def __init__(self, images, timeProperty = None, timeGenerationCallable = None, actionTag="MitkFuse3Dto4DImageMiniApp", alwaysDo=False,
                 session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None):
        CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig=actionConfig,
                               propInheritanceDict=propInheritanceDict)

        self._images = {}
        if timeGenerationCallable is not None:
            for image in images:
                self._images[timeGenerationCallable(image)] = image
        elif timeProperty is not None:
            for image in images:
                self._images[int(artefactHelper.getArtefactProperty(image, timeProperty))] = image
        else:
            raise RuntimeError('Cannot initiate MitkFuse3Dto4DImageMiniAppAction. Either "timeProperty" or'
                               ' "timeGenerationCallable" must be defined, but both are None.')

        self._addInputArtefacts(images=images)

        if self._cwd is None:
            self._cwd = os.path.dirname(AVIDUrlLocater.getExecutableURL(self._session, "MitkFuse3Dto4DImageMiniApp", actionConfig))


    def _getFirstImageKey(self):
        return next(iter(self._images.keys()))


    def _generateName(self):
        name = "Fused"
        name += "_{}".format(artefactHelper.getArtefactShortName(self._images[self._getFirstImageKey()]))
        for time in self._images:
            name += "_{}".format(time)

        return name

    def _indicateOutputs(self):
        # Specify result artefact
        self._resultArtefact = self.generateArtefact(self._images[self._getFirstImageKey()],
                                                        userDefinedProps={artefactProps.TYPE:artefactProps.TYPE_VALUE_RESULT,
                                                        artefactProps.FORMAT:artefactProps.FORMAT_VALUE_ITK},
                                                        urlHumanPrefix=self.instanceName,urlExtension='nrrd')

        return [self._resultArtefact]

    def _generateTimeInformation(self):
        times = list(self._images.keys())

        result = '{}'.format(times[0])
        for time in times[1:]:
            result += ' {}'.format(time)
        result += ' {}'.format(times[-1]*2)
        return result

    def _generateInputInformation(self):
        result = ''
        for time in self._images:
            imagePath = artefactHelper.getArtefactProperty(self._images[time], artefactProps.URL)
            result += ' "{}"'.format(imagePath)
        return result

    def _prepareCLIExecution(self):

        resultPath = artefactHelper.getArtefactProperty(self._resultArtefact, artefactProps.URL)
        osChecker.checkAndCreateDir(os.path.split(resultPath)[0])

        content = ""

        try:
            execURL = AVIDUrlLocater.getExecutableURL(self._session, "MitkFuse3Dto4DImageMiniApp", self._actionConfig)

            content += '"{}" -i{} -o "{}" -t {}'.format(execURL, self._generateInputInformation(), resultPath, self._generateTimeInformation())
        except:
            logger.error("Error for getExecutable.")
            raise

        return content


class MitkFuse3Dto4DImageMiniAppBatchAction(BatchActionBase):
    '''Batch action for MitkFuse3Dto4DImageMiniApp that produces a fused 4D image.
        @param splitProperties You can define a list of split properties (list of property names)
        to separate images. All artefacts of one action will be fused into one 4D image.'''

    def __init__(self, imageSelector, timeProperty = None, splitProperties = None,
                 actionTag="MitkFuse3Dto4DImageMiniApp", alwaysDo=False, session=None,
                 additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):

        sorter = {BatchActionBase.PRIMARY_INPUT_KEY: BaseSorter()}
        if timeProperty is not None:
            sorter = {BatchActionBase.PRIMARY_INPUT_KEY: KeyValueSorter(key=timeProperty, asNumbers=True)}

        splitter = {BatchActionBase.PRIMARY_INPUT_KEY: BaseSplitter()}
        if splitProperties is not None:
            splitter = {BatchActionBase.PRIMARY_INPUT_KEY: KeyValueSplitter(*splitProperties)}

        BatchActionBase.__init__(self, actionTag=actionTag, actionClass=MitkFuse3Dto4DImageMiniAppAction,
                                 primaryInputSelector=imageSelector,
                                 primaryAlias="images", splitter=splitter, sorter=sorter, session=session,
                                 relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps=additionalActionProps,
                                 timeProperty=timeProperty, **singleActionParameters)
