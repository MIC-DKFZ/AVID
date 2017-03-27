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

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper

from avid.common import osChecker, AVIDUrlLocater
from avid.actions import BatchActionBase
from avid.actions.cliActionBase import CLIActionBase
from avid.selectors import TypeSelector
from avid.actions.simpleScheduler import SimpleScheduler
from avid.linkers import CaseLinker

logger = logging.getLogger(__name__)

class LinearFitAction(CLIActionBase):
  '''Class that wraps the single action for MITK GenericFittingMiniApp to make a linear fit.'''

  def __init__(self, inputImage, maskImage = None, roibased = False,
               actionTag = "FFMaps", alwaysDo = False,
               session = None, additionalActionProps = None, actionConfig = None):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, None, actionConfig = None)
    self._addInputArtefacts(inputImage = inputImage, maskImage = maskImage)
     
    self._inputImage = inputImage
    self._maskImage = maskImage
    
    self._roibased = roibased
    
    self._coolstartID = artefactHelper.getArtefactProperty(inputImage, "coolstartID")
    self._coolendID = artefactHelper.getArtefactProperty(inputImage, "coolendID")
    self._targetID = artefactHelper.getArtefactProperty(inputImage, "targetID")
    
  def _generateName(self):
    name = "LinarFit_"+str(artefactHelper.getArtefactProperty(self._inputImage,artefactProps.ACTIONTAG))
    
    if self._roibased:
      name += "_roi-based_"
    else:
      name += "_pixel-based_"
      
    if self._maskImage is not None:
      name += "_masked_by_"+str(artefactHelper.getArtefactProperty(self._maskImage,artefactProps.ACTIONTAG))
    return name
   
  def _indicateOutputs(self):
    
    self._resultSlopeArtefact = self.generateArtefact(self._inputImag,
                                                 userDefinedProps={artefactProps.TYPE:artefactProps.TYPE_VALUE_RESULT,
                                                                   artefactProps.FORMAT: artefactProps.FORMAT_VALUE_ITK,
                                                                   artefactProps.OBJECTIVE:"slope"})

    path = artefactHelper.generateArtefactPath(self._session, self._resultSlopeArtefact)
    outputTemplate = self.instanceName + "." + str(artefactHelper.getArtefactProperty(self._resultSlopeArtefact,artefactProps.ID))
    resName = outputTemplate + "_slope"+os.extsep+"nrrd"
    resName = os.path.join(path, resName)
    self._resultSlopeArtefact[artefactProps.URL] = resName

    self._resultOffsetArtefact = self.generateArtefact(self._resultSlopeArtefact,
                                                 userDefinedProps={artefactProps.TYPE:artefactProps.TYPE_VALUE_RESULT,
                                                                   artefactProps.FORMAT: artefactProps.FORMAT_VALUE_ITK,
                                                                   artefactProps.OBJECTIVE:"offset"})
    resName = outputTemplate + "_offset"+os.extsep+"nrrd"
    resName = os.path.join(path, resName)
    self._resultOffsetArtefact[artefactProps.URL] = resName    

    self._outputTemplatePath = os.path.join(path, outputTemplate+os.extsep+"nrrd")
  
    return [self._resultSlopeArtefact, self._resultOffsetArtefact]

      
  def _prepareCLIExecution(self):
    
    resultPath = artefactHelper.getArtefactProperty(self._resultSlopeArtefact,artefactProps.URL)
    inputPath = artefactHelper.getArtefactProperty(self._inputImage,artefactProps.URL)
    maskPath = artefactHelper.getArtefactProperty(self._maskImage,artefactProps.URL)
      
    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])
    
    execURL = AVIDUrlLocater.getExecutableURL(self._session, "GenericFittingMiniApp", self._actionConfig)
    
    content = '"' + execURL + '" -f Linear -i "'+str(inputPath)+'" -o "'+ self._outputTemplatePath+'"'
    
    if maskPath is not None:
      content += ' -m "'+maskPath+'"'
      
    if self._roibased:
      content += "-r"

    return content



class LinearFitBatchAction(BatchActionBase):    
  '''Batch action that uses the MITK GenericFittingMiniApp to make a linear fit.'''
  
  def __init__(self,  inputSelector, maskSelector, maskLinker = CaseLinker(), roibased = False, actionTag = "LinearFit", alwaysDo = False,
               session = None, additionalActionProps = None, actionConfig = None, scheduler = SimpleScheduler()):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._inputs = inputSelector.getSelection(self._session.artefacts)
    self._masks = maskSelector.getSelection(self._session.artefacts)
    self._actionConfig = actionConfig
    self._maskLinker = maskLinker
    self._roibased = roibased

      
  def _generateActions(self):
    #filter only type result. Other artefact types are not interesting
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)
    
    inputs = self.ensureRelevantArtefacts(self._inputs, resultSelector, "4D inputs")
    masks = self.ensureRelevantArtefacts(self._masks, resultSelector, "Mask inputs")
        
    actions = list()

    for (pos,inputImage) in enumerate(inputs):
      linkedMasks = self._maskLinker.getLinkedSelection(pos,inputs,masks)
      if len(linkedMasks) == 0:
        linkedMasks = [None]
        
      for lm in linkedMasks:
        action = LinearFitAction(inputImage, lm, self._roibased, 
                              self._actionTag,
                              alwaysDo = self._alwaysDo,
                              session = self._session,
                              additionalActionProps = self._additionalActionProps,
                              miniapp =self._miniapp)
        actions.append(action)
              
    return actions
