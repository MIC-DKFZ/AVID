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
import os

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper
from avid.common.osChecker import checkAndCreateDir

from ..filter import bounding_box as bounding_box
from avid.actions import BatchActionBase
from avid.actions import SingleActionBase
from avid.selectors import TypeSelector
from avid.actions.simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)

class GenerateBBoxAction(SingleActionBase):
  '''Action that allows to generate a bounding box with a given extension arround a given mask file by the passed values in [mm].'''

  def __init__(self, maskImage, dilation = [5,5,5], outputextension = "nrrd", actionTag="GenerateBBox",
               alwaysDo=True, session=None, additionalActionProps=None, propInheritanceDict = None):
    SingleActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, propInheritanceDict = propInheritanceDict)
    self._maskImage = maskImage

    self._outputextension = outputextension
    self._dilation = dilation
    self._addInputArtefacts(maskImage=self._maskImage)
    self._resultArtefact = None

  def _generateName(self):

    name = "dilate_{}_#{}_by_{}".format(artefactHelper.getArtefactProperty(self._maskImage,artefactProps.ACTIONTAG),
                                        artefactHelper.getArtefactProperty(self._maskImage,artefactProps.TIMEPOINT),
                                        self._dilation)

    return name

  def _indicateOutputs(self):

    self._resultArtefact = self.generateArtefact(self._maskImage,
                                                 userDefinedProps={artefactProps.TYPE:artefactProps.TYPE_VALUE_RESULT},
                                                 urlHumanPrefix=self.instanceName,
                                                 urlExtension=self._outputextension)

    return [self._resultArtefact]

  def _generateOutputs(self):

    sourcePath = artefactHelper.getArtefactProperty(self._maskImage, artefactProps.URL)
    destPath = artefactHelper.getArtefactProperty(self._resultArtefact, artefactProps.URL)

    checkAndCreateDir(os.path.dirname(destPath))
    bounding_box(path_to_mask=sourcePath, output_path=destPath, dilation_in_mm=self._dilation)


class GenerateBBoxBatchAction(BatchActionBase):
  '''Batch class for the GenerateBBoxAction.'''

  def __init__(self, maskSelector, actionTag="GenerateBBox", alwaysDo=False,
               session=None, additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._inputMasks = maskSelector.getSelection(self._session.artefacts)

    self._singleActionParameters = singleActionParameters

  def _generateActions(self):
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)
    masks = self.ensureRelevantArtefacts(self._inputMasks, resultSelector, "mask input")

    actions = list()

    for mask in masks:
      action = GenerateBBoxAction(mask, actionTag = self._actionTag, alwaysDo=self._alwaysDo,
                             session=self._session,
                             additionalActionProps=self._additionalActionProps,
                             **self._singleActionParameters)
      actions.append(action)

    return actions