import os
import logging

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper

from avid.common import osChecker, AVIDUrlLocater
from . import BatchActionBase
from cliActionBase import CLIActionBase
from avid.linkers import CaseLinker
from avid.linkers import FractionLinker
from avid.selectors import TypeSelector
from simpleScheduler import SimpleScheduler
from avid.externals.matchPoint import ensureMAPRegistrationArtefact

logger = logging.getLogger(__name__)

class mapRAction(CLIActionBase):
  '''Class that wraps the single action for the tool mapR.'''

  def __init__(self, inputImage, registration = None, templateImage = None, 
               interpolator = "linear", outputExt = "nrrd", 
               actionTag = "mapR", alwaysDo = False,
               session = None, additionalActionProps = None, mapRExe = os.path.join("mapR4V","mapR4V.exe")):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps)
    self._setCaseInstanceByArtefact(inputImage,registration,templateImage)
    self._inputImage = inputImage
    self._registration = registration
    self._templateImage = templateImage
    self._interpolator = interpolator
    self._outputExt = outputExt
    self._mapRExe = mapRExe
    
    cwd = os.path.dirname(AVIDUrlLocater.getExecutableURL(self._session, "mapR", mapRExe))
    self._cwd = cwd    
    
  def _generateName(self):
    name = "map_"+str(artefactHelper.getArtefactProperty(self._inputImage,artefactProps.ACTIONTAG))\
            +"_#"+str(artefactHelper.getArtefactProperty(self._inputImage,artefactProps.TIMEPOINT))

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
    self._batchArtefact = self.generateArtefact(self._inputImage)
    self._batchArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_MISC
    self._batchArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_BAT

    path = artefactHelper.generateArtefactPath(self._session, self._batchArtefact)
    batName = name + "." + str(artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.ID)) + ".bat"
    batName = os.path.join(path, batName)
    
    self._batchArtefact[artefactProps.URL] = batName
    
    self._resultArtefact = self.generateArtefact(self._batchArtefact)
    self._resultArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._resultArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_ITK
    
    path = artefactHelper.generateArtefactPath(self._session, self._resultArtefact)
    resName = name + "." + str(artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.ID)) + os.extsep + self._outputExt
    resName = os.path.join(path, resName)
    
    self._resultArtefact[artefactProps.URL] = resName

    return [self._batchArtefact, self._resultArtefact]

      
  def _prepareCLIExecution(self):
    
    batPath = artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.URL)
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
    
    osChecker.checkAndCreateDir(os.path.split(batPath)[0])
    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])
    
    execURL = AVIDUrlLocater.getExecutableURL(self._session, "mapR", self._mapRExe)
    
    content = '"' + execURL + '"' + ' "' + inputPath + '"'
    if registrationPath is not None:
      content += ' "' + registrationPath +'"'
    
    if templatePath is not None:
      content += ' -t "' + templatePath + '"'
      
    content += ' -o "' + resultPath + '"'
    content += ' -i ' + self._interpolator + ' -p 1024 --handleMappingFailure' 
    
    if self._outputExt.lower() =="dcm" or self._outputExt.lower() == "ima":
      content += '--seriesReader dicom'
    
    with open(batPath, "w") as outputFile:
      outputFile.write(content)
      outputFile.close()
      
    return batPath      


class mapRBatchAction(BatchActionBase):    
  '''Base class for action objects that are used together with selectors and
    should therefore able to process a batch of SingleActionBased actions.'''
  
  def __init__(self,  inputSelector, registrationSelector = None, templateSelector = None,
               regLinker = FractionLinker(), templateLinker = CaseLinker(), 
               interpolator = "linear", outputExt = "nrrd", 
               actionTag = "mapR", alwaysDo = False,
               session = None, additionalActionProps = None, mapRExe = os.path.join("mapR4V","mapR4V.exe"), scheduler = SimpleScheduler()):
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
    self._interpolator = interpolator
    self._outputExt = outputExt
    self._mapRExe = mapRExe

      
  def _generateActions(self):
    #filter only type result. Other artefact types are not interesting
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)
    
    inputs = self.ensureValidArtefacts(self._inputImages, resultSelector, "mapR input")
    regs = self.ensureValidArtefacts(self._registrations, resultSelector, "mapR registrations")
    temps = self.ensureValidArtefacts(self._templateImages, resultSelector, "mapR templates")
    
    actions = list()
    
    for (pos,inputImage) in enumerate(inputs):
      linkedTemps = self._templateLinker.getLinkedSelection(pos,inputs,temps)
      if len(linkedTemps) == 0:
        linkedTemps = [None]
        
      linkedRegs = self._regLinker.getLinkedSelection(pos, inputs, regs)
      if len(linkedRegs) == 0:
        linkedRegs = [None]
      
      for lt in linkedTemps:
        for lr in linkedRegs:
          action = mapRAction(inputImage, lr, lt, self._interpolator, self._outputExt,
                              self._actionTag, alwaysDo = self._alwaysDo,
                              session = self._session,
                              additionalActionProps = self._additionalActionProps,
                              mapRExe =self._mapRExe)
          actions.append(action)
    
    return actions
