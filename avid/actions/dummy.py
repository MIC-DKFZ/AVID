print __package__

import os

from ..actions import BatchActionBase
from avid.actions import SingleActionBase
from avid.actions.cliActionBase import CLIActionBase
import avid.common.artefact as artefactHelper
import avid.common.artefact.defaultProps as artefactProps
from simpleScheduler import SimpleScheduler
from avid.common import osChecker, AVIDUrlLocater

class DummySingleAction(SingleActionBase):

  def __init__(self, artefacts, actionTag, alwaysDo = False, session = None):
    SingleActionBase.__init__(self, actionTag,alwaysDo,session)
    self._artefacts = artefacts
    
  def _generateName(self):
    name = "Dummy"
    return name
       
  def _indicateOutputs(self):
    return self._artefacts
    
  def _generateOutputs(self):
    pass
    

class DummyBatchAction(BatchActionBase):
  def __init__(self, artefacts, actionTag = 'Dummy', alwaysDo = False, scheduler = SimpleScheduler(), session = None):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session = session)
    self._artefacts = artefacts
    
  def _generateActions(self):
    actions = []
    for artefact in self._artefacts:
      action = DummySingleAction([artefact],"InternAction",self._alwaysDo, self._session)
      actions.append(action)

    return actions

  
class DummyCLIAction(CLIActionBase):
  '''Class that wraps the single action for the AVID dummy cli.'''

  def __init__(self, input,
               actionTag = "DummyCLI", alwaysDo = False,
               session = None, additionalActionProps = None, actionConfig = None):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, None, actionConfig = None)
    self._setCaseInstanceByArtefact(input)
     
    self._input = input
    
  def _generateName(self):
    name = "Dummy_of_"+str(artefactHelper.getArtefactProperty(self._input,artefactProps.ACTIONTAG))
    
    return name
   
  def _indicateOutputs(self):
    
    name = self.instanceName
                  
    self._batchArtefact = self.generateArtefact(self._input)
    self._batchArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_MISC
    self._batchArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_BAT

    path = artefactHelper.generateArtefactPath(self._session, self._batchArtefact)
    batName = name + "." + str(artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.ID))+os.extsep+"bat"
    batName = os.path.join(path, batName)
       
    self._batchArtefact[artefactProps.URL] = batName
    
    self._result = self.generateArtefact(self._batchArtefact)
    self._result[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._result[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_CSV
    
    path = artefactHelper.generateArtefactPath(self._session, self._result)
    resName = name + os.extsep+"txt"
    resName = os.path.join(path, resName)
    
    self._result[artefactProps.URL] = resName
  
    return [self._batchArtefact, self._result]

      
  def _prepareCLIExecution(self):
    
    batPath = artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.URL)
    resultPath = artefactHelper.getArtefactProperty(self._result,artefactProps.URL)
    inputPath = artefactHelper.getArtefactProperty(self._input,artefactProps.URL)
      
    osChecker.checkAndCreateDir(os.path.split(batPath)[0])
    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])
    
    execURL = AVIDUrlLocater.getExecutableURL(self._session, "CLIDummy", self._actionConfig)
    
    content = '"' + execURL + '" "'+str(resultPath)+'" "'+str(inputPath)+'" "Dummytest"'
                
    with open(batPath, "w") as outputFile:
      outputFile.write(content)
      outputFile.close()
      
    return batPath
  
  
class DummyCLIBatchAction(BatchActionBase):
  def __init__(self, artefacts, actionTag = 'DummyCLI', alwaysDo = False, scheduler = SimpleScheduler(), session = None):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session = session)
    self._artefacts = artefacts
    
  def _generateActions(self):
    actions = []
    for artefact in self._artefacts:
      action = DummyCLIAction(artefact, alwaysDo = self._alwaysDo, session = self._session)
      actions.append(action)

    return actions  
