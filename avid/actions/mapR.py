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
from avid.linkers import CaseLinker, LinkerBase
from avid.linkers import FractionLinker
from avid.selectors import TypeSelector
from simpleScheduler import SimpleScheduler
from avid.externals.matchPoint import ensureMAPRegistrationArtefact

logger = logging.getLogger(__name__)

class mapRAction(CLIActionBase):
  '''Class that wraps the single action for the tool mapR.'''

  def __init__(self, inputImage, registration = None, templateImage = None, 
               interpolator = "linear", outputExt = "nrrd", paddingValue = None,
               actionTag = "mapR", alwaysDo = False,
               session = None, additionalActionProps = None, actionConfig = None, propInheritanceDict = dict()):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig = actionConfig, propInheritanceDict = propInheritanceDict)
    self._addInputArtefacts(inputImage=inputImage, registration=registration, templateImage=templateImage)
    self._inputImage = inputImage
    self._registration = registration
    self._templateImage = templateImage
    self._interpolator = interpolator
    self._outputExt = outputExt
    self._paddingValue = paddingValue
    
    cwd = os.path.dirname(AVIDUrlLocater.getExecutableURL(self._session, "mapR", actionConfig))
    self._cwd = cwd    
    
  def _generateName(self):
    name = "map_"+str(artefactHelper.getArtefactProperty(self._inputImage,artefactProps.ACTIONTAG))

    objective = artefactHelper.getArtefactProperty(self._inputImage,artefactProps.OBJECTIVE)
    if not objective is None:
        name += '-%s'%objective

    name += "_#"+str(artefactHelper.getArtefactProperty(self._inputImage,artefactProps.TIMEPOINT))

    if self._registration is not None:
      name += "_reg_"+str(artefactHelper.getArtefactProperty(self._registration,artefactProps.ACTIONTAG))\
              +"_#"+str(artefactHelper.getArtefactProperty(self._registration,artefactProps.TIMEPOINT))
    else:
      name += "_identity"
    
    if self._templateImage is not None:
      name += "_to_"+str(artefactHelper.getArtefactProperty(self._templateImage,artefactProps.ACTIONTAG))\
              +"_#"+str(artefactHelper.getArtefactProperty(self._templateImage,artefactProps.TIMEPOINT))
    return name
   
  def _indicateOutputs(self):
    
    name = self.instanceName                    

    self._resultArtefact = self.generateArtefact(self._inputImage)
    self._resultArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._resultArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_ITK
    
    path = artefactHelper.generateArtefactPath(self._session, self._resultArtefact)
    resName = name + "." + str(artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.ID)) + os.extsep + self._outputExt
    resName = os.path.join(path, resName)
    
    self._resultArtefact[artefactProps.URL] = resName

    return [self._resultArtefact]

      
  def _prepareCLIExecution(self):
    
    resultPath = artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.URL)
    inputPath = artefactHelper.getArtefactProperty(self._inputImage,artefactProps.URL)
    templatePath = artefactHelper.getArtefactProperty(self._templateImage,artefactProps.URL)
    registrationPath = artefactHelper.getArtefactProperty(self._registration,artefactProps.URL)
    
    result = ensureMAPRegistrationArtefact(self._registration, self.generateArtefact(self._inputImage), self._session)
    if result[0]:
      if result[1] is None:
        logger.error("Mapping will fail. Given registration is not MatchPoint compatible and cannot be converted.")
      else:
        registrationPath = artefactHelper.getArtefactProperty(result[1],artefactProps.URL)
        logger.debug("Converted/Wrapped given registration artefact to be MatchPoint compatible. Wrapped artefact path: "+registrationPath)
    
    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])
    
    execURL = AVIDUrlLocater.getExecutableURL(self._session, "mapR", self._actionConfig)
    
    content = '"' + execURL + '"' + ' "' + inputPath + '"'
    if registrationPath is not None:
      content += ' "' + registrationPath +'"'
    
    if templatePath is not None:
      content += ' -t "' + templatePath + '"'
      
    content += ' -o "' + resultPath + '"'
    content += ' -i ' + self._interpolator + ' --handleMappingFailure'

    if not self._paddingValue is None:
        content += ' -p %s'%self._paddingValue
    
    if self._outputExt.lower() =="dcm" or self._outputExt.lower() == "ima":
      content += ' --seriesReader dicom'

    return content

class mapRBatchAction(BatchActionBase):
  '''Base class for action objects that are used together with selectors and
    should therefore able to process a batch of SingleActionBased actions.'''
  
  def __init__(self,  inputSelector, registrationSelector = None, templateSelector = None,
               regLinker = FractionLinker(), templateLinker = CaseLinker(), 
               actionTag = "mapR", alwaysDo = False,
               session = None, additionalActionProps = None, scheduler = SimpleScheduler(), templateRegLinker = LinkerBase(),
               **singleActionParameters):
    '''@param inputSelector Selector for the artefacts that should be mapped.
    @param registrationSelector Selector for the artefacts that specify the registration. If no registrations are
    specified, anidentity transform will be assumed.
    @param templateSelector Selector for the reference geometry that should be used to map into it. If None is
    specified, the geometry of the input will be used.
    @param regLinker Linker to select the registration that should be used on an input. Default is FractionLinker.
    @param templateLinker Linker to select the reference geometry that should be used to map an input. Default is CaseLinker.
    @param templateRegLinker Linker to select which regs (resulting from the regLinker should be used regarding
    the template that will be used. Default is LinkerBase (so every link registration will be used with every linked
    template.'''
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._inputImages = inputSelector.getSelection(self._session.inData)
    self._registrations = list()
    if registrationSelector is not None:
      self._registrations = registrationSelector.getSelection(self._session.inData)

    self._templateImages = list()
    if templateSelector is not None:
      self._templateImages = templateSelector.getSelection(self._session.inData)
    
    self._regLinker = regLinker
    self._templateLinker = templateLinker
    self._templateRegLinker = templateRegLinker

    self._singleActionParameters = singleActionParameters

      
  def _generateActions(self):
    #filter only type result. Other artefact types are not interesting
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)
    
    inputs = self.ensureRelevantArtefacts(self._inputImages, resultSelector, "mapR input")
    regs = self.ensureRelevantArtefacts(self._registrations, resultSelector, "mapR registrations")
    temps = self.ensureRelevantArtefacts(self._templateImages, resultSelector, "mapR templates")
    
    actions = list()
    
    for (pos,inputImage) in enumerate(inputs):
      linkedTemps = self._templateLinker.getLinkedSelection(pos,inputs,temps)
      if len(linkedTemps) == 0:
        linkedTemps = [None]
        
      linkedRegs = self._regLinker.getLinkedSelection(pos, inputs, regs)
      if len(linkedRegs) == 0:
        linkedRegs = [None]
      
      for (pos2, lt) in enumerate(linkedTemps):
        linkedRegsByTemp = self._templateRegLinker.getLinkedSelection(pos2, linkedTemps, linkedRegs)

        for lr in linkedRegsByTemp:
          action = mapRAction(inputImage, lr, lt,
                              actionTag = self._actionTag,
                              alwaysDo = self._alwaysDo,
                              session = self._session,
                              additionalActionProps = self._additionalActionProps,
                              **self._singleActionParameters)
          actions.append(action)
    
    return actions
