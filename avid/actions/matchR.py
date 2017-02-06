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
import time

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper

from avid.common import osChecker, AVIDUrlLocater
from . import BatchActionBase
from cliActionBase import CLIActionBase
from avid.linkers import CaseLinker
from avid.linkers import FractionLinker
from avid.selectors import TypeSelector
from simpleScheduler import SimpleScheduler

from xml.etree.ElementTree import ElementTree
import avid.common.customTags as Tag

logger = logging.getLogger(__name__)


class matchRAction(CLIActionBase):
  '''Class that wrapps the single action for the tool mapR.'''

  def __init__(self, targetImage, movingImage, algorithm, algorithmParameters=dict(), targetMask = None,  movingMask = None,
               targetIsReference = True, actionTag = "matchR", alwaysDo = False,
               session = None, additionalActionProps = None, actionConfig = None, propInheritanceDict = dict()):
       
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig = actionConfig,
                           propInheritanceDict = propInheritanceDict)
    self._addInputArtefacts(targetImage = targetImage, movingImage = movingImage, targetMask = targetMask, movingMask = movingMask)

    self._targetImage = targetImage
    self._targetMask = targetMask
    self._movingImage = movingImage
    self._movingMask = movingMask
    self._algorithm = algorithm
    self._algorithmParameters = algorithmParameters
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
    
    name = self._generateName()

    #Specify result artefact                
    self._resultArtefact = self.generateArtefact(artefactRef)
    self._resultArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._resultArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_MATCHPOINT
    
    path = artefactHelper.generateArtefactPath(self._session, self._resultArtefact)
    resName = name + "." + str(artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.ID)) + os.extsep + "mapr"
    resName = os.path.join(path, resName)
    
    self._resultArtefact[artefactProps.URL] = resName

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
      for key, value in self._algorithmParameters.iteritems():
        content += ' "' + key + "=" + value + '"'
      if self._movingMask:
        movingMaskURL = artefactHelper.getArtefactProperty(self._movingMask, artefactProps.URL)
        content += ' --moving-mask ' + movingMaskURL
      if self._targetMask:
        targetMaskURL = artefactHelper.getArtefactProperty(self._targetMask, artefactProps.URL)
        content += ' --target-mask ' + targetMaskURL

    except:
      logger.error("Error for getExecutable.")
      raise

    return content


class matchRBatchAction(BatchActionBase):
  '''Action for batch processing of the matchR.'''
  
  def __init__(self,  targetSelector, movingSelector, targetMaskSelector = None, movingMaskSelector = None,
               movingLinker = CaseLinker(), targetMaskLinker = FractionLinker(), 
               movingMaskLinker = FractionLinker(), actionTag = "matchR", alwaysDo = False,
               session = None, additionalActionProps = None, scheduler = SimpleScheduler(), **singleActionParameters):
    
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._targetImages = targetSelector.getSelection(self._session.artefacts)
    self._targetMasks = list()
    if targetMaskSelector is not None:
      self._targetMasks = targetMaskSelector.getSelection(self._session.artefacts)

    self._movingImages = movingSelector.getSelection(self._session.artefacts)
    self._movingMasks = list()
    if movingMaskSelector is not None:
      self._movingMasks = movingMaskSelector.getSelection(self._session.artefacts)
    
    self._movingLinker = movingLinker
    self._targetMaskLinker = targetMaskLinker  
    self._movingMaskLinker = movingMaskLinker
    self._singleActionParameters = singleActionParameters

  def _generateActions(self):
    #filter only type result. Other artefact types are not interesting
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)
    
    targets = self.ensureRelevantArtefacts(self._targetImages, resultSelector, "matchR targets")
    movings = self.ensureRelevantArtefacts(self._movingImages, resultSelector, "matchR movings")
    targetMasks = self.ensureRelevantArtefacts(self._targetMasks, resultSelector, "matchR target masks")
    movingMasks = self.ensureRelevantArtefacts(self._movingMasks, resultSelector, "matchR moving masks")
      
    global logger
    
    actions = list()
    
    for (pos,target) in enumerate(targets):
      linkedMovings = self._movingLinker.getLinkedSelection(pos,targets,movings)
        
      linkedTargetMasks = self._targetMaskLinker.getLinkedSelection(pos, targets, targetMasks)
      if len(linkedTargetMasks) == 0:
        linkedTargetMasks = [None]

      for (pos2,lm) in enumerate(linkedMovings):
        linkedMovingMasks = self._movingMaskLinker.getLinkedSelection(pos2, linkedMovings, movingMasks)
        if len(linkedMovingMasks) == 0:
          linkedMovingMasks = [None]

        for ltm in linkedTargetMasks:
          for lmm in linkedMovingMasks:
            action = matchRAction(target, movingImage = lm, targetMask = ltm, movingMask = lmm,
                                  actionTag=self._actionTag,
                                  alwaysDo = self._alwaysDo, session = self._session,
                                  additionalActionProps = self._additionalActionProps,
                                  **self._singleActionParameters)
            actions.append(action)
    
    return actions
