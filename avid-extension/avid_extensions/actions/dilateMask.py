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

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper
from avid.common.osChecker import checkAndCreateDir

from ..filter import dilate_mask as dilate_mask
from avid.actions import BatchActionBase
from avid.actions import SingleActionBase
from avid.selectors import TypeSelector
from avid.actions.simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)

class DilateMaskAction(SingleActionBase):
  '''Action that allows to dilate a given mask file by the passed values in [mm].'''

  def __init__(self, maskImage, dilation = [5,5,5], outputextension = "nrrd", actionTag="DilateMask",
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
    dilate_mask(path_to_mask=sourcePath, output_path=destPath, dilation_in_mm=self._dilation)


class DilateMaskActionBatchAction(BatchActionBase):
  '''Batch class for the DilateMaskAction.'''

  def __init__(self, maskSelector, actionTag="DilateMask", alwaysDo=False,
               session=None, additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._inputMasks = maskSelector.getSelection(self._session.artefacts)

    self._singleActionParameters = singleActionParameters

  def _generateActions(self):
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)
    masks = self.ensureRelevantArtefacts(self._inputMasks, resultSelector, "mask input")

    actions = list()

    for mask in masks:
      action = DilateMaskAction(mask, actionTag = self._actionTag, alwaysDo=self._alwaysDo,
                             session=self._session,
                             additionalActionProps=self._additionalActionProps,
                             **self._singleActionParameters)
      actions.append(action)

    return actions