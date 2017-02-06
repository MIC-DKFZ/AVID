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
from . import BatchActionBase
from cliActionBase import CLIActionBase
from avid.linkers import FractionLinker
from avid.selectors import TypeSelector
from avid.sorter import TimePointSorter
from simpleScheduler import SimpleScheduler
from doseMap import _getArtefactLoadStyle 
from avid.externals.matchPoint import ensureMAPRegistrationArtefact
import avid.common.demultiplexer as demux

logger = logging.getLogger(__name__)

class ImageAccAction(CLIActionBase):
  '''Class that wraps the single action for the tool imageAcc.'''

  def __init__(self, image1, image2, registration = None, weight1 = None,
               weight2 = None, interpolator = "linear", operator="+",  outputExt = "nrrd",
               actionTag = "imageAcc", alwaysDo = False,
               session = None, additionalActionProps = None, actionConfig = None, propInheritanceDict = dict()):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig = actionConfig,
                           propInheritanceDict = propInheritanceDict)
    self._addInputArtefacts(image1 = image1, image2 = image2, registration=registration)
        
    self._image1 = image1
    self._registration = registration
    self._image2 = image2
    self._weight1 = weight1
    self._weight2 = weight2
    self._interpolator = interpolator
    self._operator = operator
    self._outputExt = outputExt
    self._accumulationNR = additionalActionProps[artefactProps.ACC_ELEMENT]
    self._resultArtefact = None;
    
    
  def _generateName(self):
    #need to define the outputs
    name = "imageAcc_"+str(artefactHelper.getArtefactProperty(self._image1,artefactProps.ACTIONTAG))\
            +"_#"+str(artefactHelper.getArtefactProperty(self._image1,artefactProps.TIMEPOINT))

    if (self._operator == "+"):
      name += "_a_"
    elif (self._operator == "*"):
      name += "_m_"
    else:
      logger.error("operator %s not known.", self._operator)
      raise

    name += str(artefactHelper.getArtefactProperty(self._image2,artefactProps.ACTIONTAG))\
            +"_#"+str(artefactHelper.getArtefactProperty(self._image2,artefactProps.TIMEPOINT))

    if self._registration is not None:
      name += "_by_"+str(artefactHelper.getArtefactProperty(self._registration,artefactProps.ACTIONTAG))\
              +"_#"+str(artefactHelper.getArtefactProperty(self._registration,artefactProps.TIMEPOINT))
    else:
      name += "_by_identity"

    name += "_"+str(self._accumulationNR)
    return name
   
  def _indicateOutputs(self):
    
    if self._resultArtefact is None:
      name = self.instanceName

      self._resultArtefact = self.generateArtefact(self._image2)
      self._resultArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
      self._resultArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_ITK
      
      path = artefactHelper.generateArtefactPath(self._session, self._resultArtefact)
      resName = name + "." + str(artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.ID)) + os.extsep + self._outputExt
      resName = os.path.join(path, resName)
      
      self._resultArtefact[artefactProps.URL] = resName

    return [self._resultArtefact]
 
                
  def _prepareCLIExecution(self):
    
    resultPath = artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.URL)
    image1Path = artefactHelper.getArtefactProperty(self._image1,artefactProps.URL)
    image2Path = artefactHelper.getArtefactProperty(self._image2,artefactProps.URL)
    registrationPath = artefactHelper.getArtefactProperty(self._registration,artefactProps.URL)
    
    result = ensureMAPRegistrationArtefact(self._registration, self.generateArtefact(self._image2), self._session)
    if result[0]:
      if result[1] is None:
        logger.error("Image accumulation will fail. Given registration is not MatchPoint compatible and cannot be converted.")
      else:
        registrationPath = artefactHelper.getArtefactProperty(result[1],artefactProps.URL)
        logger.debug("Converted/Wrapped given registration artefact to be MatchPoint compatible. Wrapped artefact path: "+registrationPath)    
    
    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])
    
    execURL = AVIDUrlLocater.getExecutableURL(self._session, "DoseAcc", self._actionConfig)
    
    content = '"'+execURL + '"' + ' "' + image1Path + '"'+ ' "' + image2Path + '"' + ' "' + resultPath + '"'

    if registrationPath is not None:
      content += ' -r "' + registrationPath +'"'
    
    if self._weight1 is not None:
      content += ' --weight1 "' + str(self._weight1) + '"'

    if self._weight2 is not None:
      content += ' --weight2 "' + str(self._weight2) + '"'
      
    content += ' --interpolator ' + self._interpolator

    content += ' --operator ' + self._operator
    
    content += ' --loadStyle1 ' + _getArtefactLoadStyle(self._image1)
    content += ' --loadStyle2 ' + _getArtefactLoadStyle(self._image2)

    return content


class ImageAccBatchAction(BatchActionBase):    
  '''This action accumulates a whole selection of images and stores the result.'''
  
  def __init__(self,  imageSelector, registrationSelector = None, regLinker = FractionLinker(),
               imageSorter = TimePointSorter(), imageSplitProperty = None,
               actionTag = "imageAcc", alwaysDo = False,
               session = None, additionalActionProps = None, **singleActionParameters):
    BatchActionBase.__init__(self, actionTag, alwaysDo, SimpleScheduler(), session, additionalActionProps)

    self._images = imageSelector.getSelection(self._session.inData)

    self._registrations = list()
    if registrationSelector is not None:
      self._registrations = registrationSelector.getSelection(self._session.inData)
 
    self._regLinker = regLinker
    self._imageSorter = imageSorter
    self._imageSplitProperty = imageSplitProperty
    self._singleActionParameters = singleActionParameters

        
  def _generateActions(self):
    #filter only type result. Other artefact types are not interesting
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)
    
    allImages = self.ensureRelevantArtefacts(self._images, resultSelector, "imageAcc images")
    regs = self.ensureRelevantArtefacts(self._registrations, resultSelector, "imageAcc regs")
        
    splittedImages = list()
    
    if self._imageSplitProperty is not None:
      splitDict = demux.getSelectors(str(self._imageSplitProperty), workflowData = allImages)
      for splitID in splitDict:
        relevantImageSelector = splitDict[splitID]
        relevantInputs = relevantImageSelector.getSelection(allImages)
        splittedImages.append(relevantInputs)
    else:
      splittedImages.append(allImages)        
    
    actions = list()
       
    for images in splittedImages:
      images = self._imageSorter.sortSelection(images)
      for (pos,image) in enumerate(images):
        weight2 = 1.0/len(images) 
          
        linkedRegs = self._regLinker.getLinkedSelection(pos, images, regs)
        lReg = None
        if len(linkedRegs) > 0:
          lReg = linkedRegs[0]
          if len(linkedRegs) > 1:
            logger.warning("Improper selection of registrations. Multiple registrations for one image/fraction selected. Action assumes only one registration linked per image. Use first registration. Drop other registrations. Used registration: %s", lReg)
                 
        additionalActionProps = {artefactProps.ACC_ELEMENT: str(pos)}
        
        if self._additionalActionProps is not None:
          additionalActionProps.update(self._additionalActionProps)
          
        if pos == 0:
          # first element should be handled differently
          action = ImageAccAction(image, image, lReg, 0.0, weight2,
                                  actionTag = self._actionTag, alwaysDo = self._alwaysDo,
                                  session = self._session,
                                  additionalActionProps = additionalActionProps,
                                  **self._singleActionParameters)
        else:
          interimImageArtefact = actions[-1]._resultArtefact #take the image result of the last action
          action = ImageAccAction(interimImageArtefact, image, lReg, 1.0, weight2,
                                  actionTag = self._actionTag, alwaysDo = self._alwaysDo,
                                  session = self._session,
                                  additionalActionProps = additionalActionProps,
                                  **self._singleActionParameters)
          
        action._indicateOutputs() #call to ensure the result artefact is defined
        actions.append(action)
    
    return actions
  