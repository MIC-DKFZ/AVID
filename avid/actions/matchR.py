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

def EnsureSingleArtefact (artefacts, name):
    if artefacts is None:
        return None
    if len(artefacts) == 0:
        return None
    if len(artefacts)>1:
        logger.warning("Action only supports one artefact as %s. Use first one.".format(name))
    return artefacts[0]

class matchRAction(CLIActionBase):
  '''Class that wrapps the single action for the tool mapR.'''

  def __init__(self, targetImage, movingImage, algorithm, algorithmParameters = None, targetMask = None,  movingMask = None,
               targetPointSet = None, movingPointSet = None,
               targetIsReference = True, actionTag = "matchR", alwaysDo = False,
               session = None, additionalActionProps = None, actionConfig = None, propInheritanceDict = None):
       
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig = actionConfig,
                           propInheritanceDict = propInheritanceDict)
    self._addInputArtefacts(targetImage = targetImage, movingImage = movingImage, targetMask = targetMask,
                            movingMask = movingMask, targetPointSet = targetPointSet, movingPointSet = movingPointSet)

    self._targetImage = EnsureSingleArtefact(targetImage, "target");
    self._targetMask = EnsureSingleArtefact(targetMask, "targetMask");
    self._targetPointSet = EnsureSingleArtefact(targetPointSet, "targetPointSet");
    self._movingImage = EnsureSingleArtefact(movingImage, "moving");
    self._movingMask = EnsureSingleArtefact(movingMask, "movingMask");
    self._movingPointSet = EnsureSingleArtefact(movingPointSet, "movingPointSet");

    self._algorithm = algorithm
    self._algorithmParameters = algorithmParameters
    if self._algorithmParameters is None:
      self._algorithmParameters = dict()

    self._targetIsReference = targetIsReference

    cwd = os.path.dirname(AVIDUrlLocater.getExecutableURL(self._session, "matchR", actionConfig))
    self._cwd = cwd
  
  
  def _generateName(self):
    name = "reg_"+str(artefactHelper.getArtefactProperty(self._movingImage,artefactProps.ACTIONTAG))\
            +"_#"+str(artefactHelper.getArtefactProperty(self._movingImage,artefactProps.TIMEPOINT))

    if self._movingMask is not None:
      name += "_"+str(artefactHelper.getArtefactProperty(self._movingMask,artefactProps.ACTIONTAG))

    name += "_to_"+str(artefactHelper.getArtefactProperty(self._targetImage,artefactProps.ACTIONTAG))\
            +"_#"+str(artefactHelper.getArtefactProperty(self._targetImage,artefactProps.TIMEPOINT))

    if self._targetMask is not None:
      name += "_"+str(artefactHelper.getArtefactProperty(self._targetMask,artefactProps.ACTIONTAG))
      
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
      execURL = AVIDUrlLocater.getExecutableURL(self._session, "matchR", self._actionConfig)
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
               movingLinker = None, targetMaskLinker = FractionLinker(),
               movingMaskLinker = FractionLinker(), targetPSLinker = FractionLinker(),
               movingPSLinker = FractionLinker(), actionTag = "matchR",
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
