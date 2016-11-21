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
import avid.externals.virtuos as virtuos
from avid.externals.matchPoint import ensureMAPRegistrationArtefact

logger = logging.getLogger(__name__)

class DoseMapAction(CLIActionBase):
  '''Class that wraps the single action for the tool doseMap.'''

  def __init__(self, inputDose, registration = None, templateDose = None, 
               interpolator = "linear", outputExt = "nrrd", 
               actionTag = "doseMap", alwaysDo = False,
               session = None, additionalActionProps = None, actionConfig = None, propInheritanceDict = dict()):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig = actionConfig,
                           propInheritanceDict=propInheritanceDict)
    self._addInputArtefacts(inputDose=inputDose, registration=registration, templateDose=templateDose)

    self._inputDose = inputDose
    self._registration = registration
    self._templateDose = templateDose
    self._interpolator = interpolator
    self._outputExt = outputExt
    
    cwd = os.path.dirname(AVIDUrlLocater.getExecutableURL(self._session, "DoseMap", actionConfig))
    self._cwd = cwd    
    

  def _generateName(self):
    name = "doseMap_"+str(artefactHelper.getArtefactProperty(self._inputDose,artefactProps.ACTIONTAG))\
            +"_#"+str(artefactHelper.getArtefactProperty(self._inputDose,artefactProps.TIMEPOINT))

    if self._registration is not None:
      name += "_reg_"+str(artefactHelper.getArtefactProperty(self._registration,artefactProps.ACTIONTAG))\
              +"_#"+str(artefactHelper.getArtefactProperty(self._registration,artefactProps.TIMEPOINT))
    else:
      name += "_identity"
    
    if self._templateDose is not None:
      name += "_to_"+str(artefactHelper.getArtefactProperty(self._templateDose,artefactProps.ACTIONTAG))\
              +"_#"+str(artefactHelper.getArtefactProperty(self._templateDose,artefactProps.TIMEPOINT))

    return name

   
  def _indicateOutputs(self):    
    name = self.instanceName
                    
    self._batchArtefact = self.generateArtefact(self._inputDose)
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
    inputPath = artefactHelper.getArtefactProperty(self._inputDose,artefactProps.URL)
    templatePath = artefactHelper.getArtefactProperty(self._templateDose,artefactProps.URL)
    registrationPath = artefactHelper.getArtefactProperty(self._registration,artefactProps.URL)

    result = ensureMAPRegistrationArtefact(self._registration, self.generateArtefact(self._inputDose), self._session)
    if result[0]:
      if result[1] is None:
        logger.error("Mapping will fail. Given registration is not MatchPoint compatible and cannot be converted.")
      else:
        registrationPath = artefactHelper.getArtefactProperty(result[1],artefactProps.URL)
        logger.debug("Converted/Wrapped given registration artefact to be MatchPoint compatible. Wrapped artefact path: "+registrationPath)
    
    osChecker.checkAndCreateDir(os.path.split(batPath)[0])
    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])
    
    execURL = AVIDUrlLocater.getExecutableURL(self._session, "DoseMap", self._actionConfig)
    
    content = '"' + execURL + '"' + ' "' + inputPath + '"' + ' "' + resultPath + '"'
    if registrationPath is not None:
      content += ' --regFileName "' + registrationPath +'"'
    
    if templatePath is not None:
      content += ' --refDoseFile "' + templatePath + '"'
      content += ' --refDoseLoadStyle ' + _getArtefactLoadStyle(self._templateDose)
      
    content += ' --interpolator ' + self._interpolator
    
    content += ' --inputDoseLoadStyle ' + _getArtefactLoadStyle(self._inputDose)

    
    with open(batPath, "w") as outputFile:
      outputFile.write(content)
      outputFile.close()
      
    return batPath      


def _getArtefactLoadStyle(artefact):
  'deduce the load style parameter for an artefact that should be input'
  aPath = artefactHelper.getArtefactProperty(artefact,artefactProps.URL)
  aFormat = artefactHelper.getArtefactProperty(artefact,artefactProps.FORMAT)
  
  result = ""
  
  if aFormat == artefactProps.FORMAT_VALUE_ITK:
    result = aFormat
  elif aFormat == artefactProps.FORMAT_VALUE_DCM:
    result = "dicom"
  elif aFormat == artefactProps.FORMAT_VALUE_HELAX_DCM:
    result = "helax"
  elif aFormat == artefactProps.FORMAT_VALUE_VIRTUOS:
    result = "virtuos"
    #for virtuos we also need the plan information, check if we have the according artefact property
    plan = artefactHelper.getArtefactProperty(artefact,artefactProps.VIRTUOS_PLAN_REF)

    if not plan:
      #we assume as fall back that the plan has the same path except the extension
      plan = virtuos.stripFileExtensions(aPath)+os.extsep+"pln"
        
    result = result + ' "' + plan + '"'
  else:
    logger.info("No load style known for artefact format: %s", aFormat)
    
  return result


class DoseMapBatchAction(BatchActionBase):    
  '''Base class for action objects that are used together with selectors and
    should therefore able to process a batch of SingleActionBased actions.'''
  
  def __init__(self,  inputSelector, registrationSelector = None, templateSelector = None,
               regLinker = FractionLinker(), templateLinker = CaseLinker(), 
               actionTag = "doseMap", alwaysDo = False,
               session = None, additionalActionProps = None, scheduler = SimpleScheduler(),
               **singleActionParameters):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._inputDoses = inputSelector.getSelection(self._session.inData)
    self._registrations = list()
    if registrationSelector is not None:
      self._registrations = registrationSelector.getSelection(self._session.inData)

    self._templateDoses = list()
    if templateSelector is not None:
      self._templateDoses = templateSelector.getSelection(self._session.inData)
    
    self._regLinker = regLinker
    self._templateLinker = templateLinker  
    self._singleActionParameters = singleActionParameters

      
  def _generateActions(self):
    #filter only type result. Other artefact types are not interesting
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)
    
    inputs = self.ensureValidArtefacts(self._inputDoses, resultSelector, "doseMap doses")
    regs = self.ensureValidArtefacts(self._registrations, resultSelector, "doseMap registrations")
    temps = self.ensureValidArtefacts(self._templateDoses, resultSelector, "doseMap templates")
       
    actions = list()
    
    for (pos,inputDose) in enumerate(inputs):
      linkedTemps = self._templateLinker.getLinkedSelection(pos,inputs,temps)
      if len(linkedTemps) == 0:
        linkedTemps = [None]
        
      linkedRegs = self._regLinker.getLinkedSelection(pos, inputs, regs)
      if len(linkedRegs) == 0:
        linkedRegs = [None]
      
      for lt in linkedTemps:
        for lr in linkedRegs:
          action = DoseMapAction(inputDose, registration=lr, templateDose=lt,
                              actionTag=self._actionTag, alwaysDo = self._alwaysDo,
                              session = self._session,
                              additionalActionProps = self._additionalActionProps,
                              **self._singleActionParameters)
          actions.append(action)
    
    return actions