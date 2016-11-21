import os
import logging

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper

from avid.common import osChecker, AVIDUrlLocater
from . import BatchActionBase
from cliActionBase import CLIActionBase
from avid.linkers import CaseLinker
from avid.selectors import TypeSelector
from simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)


class RegVarToolAction(CLIActionBase):
  '''Class that wrapps the single action for the tool regVarTool.'''

  def __init__(self, reg, instanceNr, algorithmDLL, parameters = None, templateImage = None, actionTag = "regVarTool", alwaysDo = False,
               session = None, additionalActionProps = None, actionConfig = None, propInheritanceDict = dict()):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig=actionConfig, propInheritanceDict = propInheritanceDict)
    self._addInputArtefacts(reg = reg)
    self._reg = reg
    self._algorithmDLL = algorithmDLL
    self._parameters = parameters
    self._templateImage = templateImage
    self._instanceNr = instanceNr
    
    if self._caseInstance is not None and not instanceNr == self._caseInstance:
      logger.warning("Case instance conflict between input artefacts (%s) and instance that should be defined by action (%s).",self._caseInstance, instanceNr)
  
  def _generateName(self):
    name = "reg_var_"+str(self._instanceNr)+"_of_"+str(artefactHelper.getArtefactProperty(self._reg,artefactProps.ACTIONTAG))\
            +"_#"+str(artefactHelper.getArtefactProperty(self._reg,artefactProps.TIMEPOINT))
     
    return name
    
  def _indicateOutputs(self):
    
    artefactRef = self._reg
    
    name = self._generateName()
    
    #Specify batch artefact                
    self._batchArtefact = self.generateArtefact(artefactRef)
    self._batchArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_MISC
    self._batchArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_BAT#
    self._batchArtefact[artefactProps.CASEINSTANCE] = str(self._instanceNr)

    path = artefactHelper.generateArtefactPath(self._session, self._batchArtefact)
    batName = name + "." + str(artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.ID)) + os.extsep + "bat"
    batName = os.path.join(path, batName)
    
    self._batchArtefact[artefactProps.URL] = batName
    
    #Specify result artefact                
    self._resultArtefact = self.generateArtefact(self._batchArtefact)
    self._resultArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._resultArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_MATCHPOINT
    self._resultArtefact[artefactProps.CASEINSTANCE] = str(self._instanceNr)
    
    path = artefactHelper.generateArtefactPath(self._session, self._resultArtefact)
    resName = name + "." + str(artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.ID)) + os.extsep + "mapr"
    resName = os.path.join(path, resName)
    
    self._resultArtefact[artefactProps.URL] = resName

    return [self._batchArtefact, self._resultArtefact]
        
  def _prepareCLIExecution(self):
    
    batPath = artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.URL)
    resultPath = artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.URL)
    regPath = artefactHelper.getArtefactProperty(self._reg, artefactProps.URL)
    templatePath = artefactHelper.getArtefactProperty(self._templateImage,artefactProps.URL)
    
    osChecker.checkAndCreateDir(os.path.split(batPath)[0])
    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])
    if self._parameters is not None:
      parametersAsString = self._toString(self._parameters)
    
    execURL = AVIDUrlLocater.getExecutableURL(self._session, "RegVarTool", self._actionConfig)
    
    content = '"' + execURL + '"'
    content += ' -a ' + '"' + self._algorithmDLL + '"'
    content += ' -o ' + '"' + resultPath + '"'
    content += ' -r ' + '"' + regPath + '"'
    if self._parameters is not None:
      content += ' -p ' + parametersAsString
    if templatePath is not None:
      content += ' -i ' + '"' + templatePath + '"'
    
    with open(batPath, "w") as outputFile:
      outputFile.write(content)
      
    return batPath      

  def _toString(self, parameters):
    parametersString = ""
    for key, value in parameters.iteritems():
      parametersString += key + " " + value
      parametersString += " "
    parametersString = parametersString.strip()
    return parametersString



class RegVarToolBatchAction(BatchActionBase):
  '''Action for batch processing of the regVarTool.'''

  def __init__(self, regs, variationCount, templateSelector = None,
               templateLinker = CaseLinker(),
               actionTag = "regVarTool", alwaysDo = False,
               session = None, additionalActionProps = None, scheduler = SimpleScheduler(),
               **singleActionParameters):
    
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._regs = regs.getSelection(self._session.inData)

    self._templateImages = list()
    if templateSelector is not None:
      self._templateImages = templateSelector.getSelection(self._session.inData)
    self._templateLinker = templateLinker
    
    self._variationCount = variationCount
    self._singleActionParameters = singleActionParameters

      
  def _generateActions(self):
    #filter only type result. Other artefact types are not interesting
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)
    
    regs = self.ensureValidArtefacts(self._regs, resultSelector, "regVarTool regs")
    temps = self.ensureValidArtefacts(self._templateImages, resultSelector, "regVarTool templates")
      
    actions = list()
    
    for (regpos, reg) in enumerate(regs):
      linkedTemps = self._templateLinker.getLinkedSelection(regpos,regs,temps)
      if len(linkedTemps) == 0:
        linkedTemps = [None]

      for pos in range(0, self._variationCount):
        for lt in linkedTemps:
          action = RegVarToolAction(reg, pos,
                                    templateImage = lt,
                                    actionTag = self._actionTag,
                                    alwaysDo = self._alwaysDo,
                                    session = self._session,
                                    additionalActionProps = self._additionalActionProps,
                                    **self._singleActionParameters)
          actions.append(action)
    
    return actions
