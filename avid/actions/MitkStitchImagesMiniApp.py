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

INTERPOLATOR_NN = 0
INTERPOLATOR_LINEAR = 1
STITCH_STRATEGY_MEAN = 0
STITCH_STRATEGY_BORDER_DISTANCE = 1

class MitkStitchImagesMiniAppAction(CLIActionBase):
    '''Class that wrapps the single action for the tool MitkStitchImagesMiniApp.'''

    def __init__(self, images, template, registrations = None, actionTag="MitkStitchImagesMiniApp",
                 paddingValue = None, stitchStrategy=None, interpolator=None, alwaysDo=False,
                 session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None):
        CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig=actionConfig,
                               propInheritanceDict=propInheritanceDict)

        self._images = images
        self._registrations = registrations
        self._template = self._ensureSingleArtefact(template, "template");
        self._paddingValue = paddingValue
        self._stitchStrategy = stitchStrategy
        self._interpolator = interpolator

        self._addInputArtefacts(images=images, registrations=registrations, template=template)

        if self._cwd is None:
            self._cwd = os.path.dirname(AVIDUrlLocater.getExecutableURL(self._session, "MitkStitchImagesMiniApp", actionConfig))


    def _generateName(self):
        name = "Stitched"
        if len(self._registrations) != 0:
            name += "_withReg"

        return name

    def _indicateOutputs(self):
        # Specify result artefact
        self._resultArtefact = self.generateArtefact(self._images[0],
                                                        userDefinedProps={artefactProps.TYPE:artefactProps.TYPE_VALUE_RESULT,
                                                        artefactProps.FORMAT:artefactProps.FORMAT_VALUE_ITK},
                                                        urlHumanPrefix=self.instanceName,urlExtension='nrrd')
        return [self._resultArtefact]

    def _generateInputInformation(self):
        result = ''
        for image in self._images:
            imagePath = artefactHelper.getArtefactProperty(image, artefactProps.URL)
            result += ' "{}"'.format(imagePath)
        return result

    def _generateRegInformation(self):
        result = ''
        for reg in self._registrations:
            regPath = artefactHelper.getArtefactProperty(reg, artefactProps.URL)
            result += ' "{}"'.format(regPath)
        return result

    def _prepareCLIExecution(self):

        resultPath = artefactHelper.getArtefactProperty(self._resultArtefact, artefactProps.URL)
        osChecker.checkAndCreateDir(os.path.split(resultPath)[0])

        templatePath = artefactHelper.getArtefactProperty(self._template, artefactProps.URL)

        content = ""

        try:
            execURL = AVIDUrlLocater.getExecutableURL(self._session, "MitkStitchImagesMiniApp", self._actionConfig)

            content += '"{}" -i{} -o "{}" -t "{}"'.format(execURL, self._generateInputInformation(), resultPath, templatePath)
            if len(self._registrations)>0:
                content += ' -r {}'.format(self._generateRegInformation())
            if self._interpolator is not None:
                content += ' --interpolator {}'.format(self._interpolator)
            if self._paddingValue is not None:
                content += ' -p {}'.format(self._paddingValue)
            if self._stitchStrategy is not None:
                content += ' -s {}'.format(self._stitchStrategy)
        except:
            logger.error("Error for getExecutable.")
            raise

        return content


class MitkStitchImagesMiniAppBatchAction(BatchActionBase):
    '''Batch action for MitkStitchImagesMiniApp that produces a stitched 4D image.
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
                 actionTag="MitkStitchImagesMiniApp", session=None,
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

        BatchActionBase.__init__(self, actionTag=actionTag, actionClass=MitkStitchImagesMiniAppAction,
                                 primaryInputSelector=imagesSelector,
                                 primaryAlias="images", additionalInputSelectors = additionalInputSelectors,
                                 linker = linker, dependentLinker=dependentLinker, splitter=splitter, sorter=sorter,
                                 session=session, relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps=additionalActionProps,
                                 **singleActionParameters)
