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

from builtins import str
import os
import logging
import time

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper

from avid.common import osChecker, AVIDUrlLocater
from avid.externals.matchPoint import FORMAT_VALUE_MATCHPOINT

from . import BatchActionBase
from .cliActionBase import CLIActionBase
from avid.linkers import CaseLinker
from avid.linkers import FractionLinker
from avid.selectors import TypeSelector
from .simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)

class matchRAction(CLIActionBase):
  '''Class that wrapps the single action for the tool mapR.'''

  def __init__(self, targetImage, movingImage, algorithm, algorithmParameters = None, targetMask = None,  movingMask = None,
               targetPointSet = None, movingPointSet = None,
               targetIsReference = True, actionTag = "matchR", alwaysDo = False,
               session = None, additionalActionProps = None, actionConfig = None, propInheritanceDict = None, cli_connector = None):
       
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionID= "matchR", actionConfig = actionConfig,
                           propInheritanceDict = propInheritanceDict, cli_connector = cli_connector)
    self._addInputArtefacts(targetImage = targetImage, movingImage = movingImage, targetMask = targetMask,
                            movingMask = movingMask, targetPointSet = targetPointSet, movingPointSet = movingPointSet)

    self._targetImage = self._ensureSingleArtefact(targetImage, "target");
    self._targetMask = self._ensureSingleArtefact(targetMask, "targetMask");
    self._targetPointSet = self._ensureSingleArtefact(targetPointSet, "targetPointSet");
    self._movingImage = self._ensureSingleArtefact(movingImage, "moving");
    self._movingMask = self._ensureSingleArtefact(movingMask, "movingMask");
    self._movingPointSet = self._ensureSingleArtefact(movingPointSet, "movingPointSet");

    self._algorithm = algorithm
    self._algorithmParameters = algorithmParameters
    if self._algorithmParameters is None:
      self._algorithmParameters = dict()

    self._targetIsReference = targetIsReference
  
  def _generateName(self):
    name = "reg_"+artefactHelper.getArtefactShortName(self._movingImage)

    if self._movingMask is not None:
      name += "_"+artefactHelper.getArtefactShortName(self._movingMask)

    name += "_to_"+artefactHelper.getArtefactShortName(self._targetImage)

    if self._targetMask is not None:
      name += "_"+artefactHelper.getArtefactShortName(self._targetMask)
      
    return name
    
  def _indicateOutputs(self):
    
    artefactRef = self._targetImage
    if not self._targetIsReference:
      artefactRef = self._movingImage

    #Specify result artefact                
    self._resultArtefact = self.generateArtefact(artefactRef,
                                                 userDefinedProps={artefactProps.TYPE:artefactProps.TYPE_VALUE_RESULT,
                                                                   artefactProps.FORMAT: FORMAT_VALUE_MATCHPOINT},
                                                 urlHumanPrefix=self._generateName(),
                                                 urlExtension='mapr')
    return [self._resultArtefact]

        
  def _prepareCLIExecution(self):
    
    resultPath = artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.URL)

    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])
      
    try:
      execURL = self._cli_connector.get_executable_url(self._session, self._actionID, self._actionConfig)
      targetImageURL = artefactHelper.getArtefactProperty(self._targetImage,artefactProps.URL)
      movingImageURL = artefactHelper.getArtefactProperty(self._movingImage, artefactProps.URL)
    
      content = '"' + execURL + '"'
      content += ' "' + movingImageURL + '"'
      content +=  ' "' + targetImageURL + '"'
      content +=  ' "' + self._algorithm + '"'
      content += ' --output "' + resultPath + '"'
      if self._algorithmParameters:
        content += ' --parameters'
        for key, value in self._algorithmParameters.items():
          content += ' "' + key + '=' + value + '"'
        content += ' "WorkingDirectory=' + os.path.join(self._session._rootPath, artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.ID)) +'"'
      if self._movingMask:
        movingMaskURL = artefactHelper.getArtefactProperty(self._movingMask, artefactProps.URL)
        content += ' --moving-mask "' + movingMaskURL + '"'
      if self._targetMask:
        targetMaskURL = artefactHelper.getArtefactProperty(self._targetMask, artefactProps.URL)
        content += ' --target-mask "' + targetMaskURL + '"'
      if self._movingPointSet:
        movingPSURL = artefactHelper.getArtefactProperty(self._movingPointSet, artefactProps.URL)
        content += ' --moving-pointset "' + movingPSURL + '"'
      if self._targetPointSet:
        targetPSURL = artefactHelper.getArtefactProperty(self._targetPointSet, artefactProps.URL)
        content += ' --target-pointset "' + targetPSURL + '"'

    except:
      logger.error("Error for getExecutable.")
      raise

    return content


class matchRBatchAction(BatchActionBase):
  '''Action for batch processing of the matchR.'''
  
  def __init__(self,  targetSelector, movingSelector, targetMaskSelector = None, movingMaskSelector = None,
               targetPointSetSelector=None, movingPointSetSelector=None,
               movingLinker = None, targetMaskLinker = None,
               movingMaskLinker = None, targetPSLinker = None,
               movingPSLinker = None, actionTag = "matchR",
               session = None, additionalActionProps = None, scheduler = SimpleScheduler(), **singleActionParameters):

    if movingLinker is None:
      movingLinker = CaseLinker()
    if targetMaskLinker is None:
      targetMaskLinker = FractionLinker()
    if movingMaskLinker is None:
      movingMaskLinker = FractionLinker()
    if targetPSLinker is None:
      targetPSLinker = FractionLinker()
    if movingPSLinker is None:
      movingPSLinker = FractionLinker()

    additionalInputSelectors = {"movingImage": movingSelector, "targetMask": targetMaskSelector,
                                "movingMask": movingMaskSelector,"targetPointSet": targetPointSetSelector,
                                "movingPointSet":movingPointSetSelector}
    linker = {"movingImage": movingLinker, "targetMask": targetMaskLinker,
              "targetPointSet": targetPSLinker}
    dependentLinker = {"movingMask": ("movingImage",movingMaskLinker),
                       "movingPointSet":("movingImage",movingPSLinker)}

    BatchActionBase.__init__(self, actionTag= actionTag, actionClass=matchRAction, primaryInputSelector= targetSelector,
                             primaryAlias="targetImage", additionalInputSelectors = additionalInputSelectors,
                             linker = linker, dependentLinker=dependentLinker, session= session,
                             relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                             scheduler=scheduler, additionalActionProps = additionalActionProps, **singleActionParameters)
