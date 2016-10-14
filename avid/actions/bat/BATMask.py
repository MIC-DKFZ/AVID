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

class BATMaskAction(CLIActionBase):
  '''Class that wraps the single action for Matlab script BATMask.'''

  def __init__(self, lungImage, thoraxImage, scriptDirectory,
               actionTag = "BATMask", alwaysDo = False,
               session = None, additionalActionProps = None, matlab = os.path.join("matlab","matlab.exe")):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, scriptDirectory)
    self._setCaseInstanceByArtefact(lungImage, thoraxImage)
     
    self._lungImage = lungImage
    self._thoraxImage = thoraxImage
    
    self._matlab = matlab
    
  def _generateName(self):
    name = "BATMask_"+str(artefactHelper.getArtefactProperty(self._lungImage,artefactProps.ACTIONTAG))+"_with_"+str(artefactHelper.getArtefactProperty(self._thoraxImage,artefactProps.ACTIONTAG))
    return name
   
  def _indicateOutputs(self):
    
    name = self.instanceName
                 
    self._batchArtefact = self.generateArtefact(self._lungImage)
    self._batchArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_MISC
    self._batchArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_BAT

    path = artefactHelper.generateArtefactPath(self._session, self._batchArtefact)
    batName = name + "." + str(artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.ID)) + ".bat"
    batName = os.path.join(path, batName)
    
    self._batchArtefact[artefactProps.URL] = batName
    
    self._resultArtefact = self.generateArtefact(self._batchArtefact)
    self._resultArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._resultArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_ITK
    self._resultArtefact[artefactProps.OBJECTIVE] = "thorax"
    
    path = artefactHelper.generateArtefactPath(self._session, self._resultArtefact)
    resName = name + str(artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.ID)) + os.extsep + "nrrd"
    resName = os.path.join(path, resName)
    
    self._resultArtefact[artefactProps.URL] = resName    
   
    return [self._batchArtefact, self._resultArtefact]

      
  def _prepareCLIExecution(self):
    
    batPath = artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.URL)
    resultPath = artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.URL)
    lungPath = artefactHelper.getArtefactProperty(self._lungImage,artefactProps.URL)
    thoraxPath = artefactHelper.getArtefactProperty(self._thoraxImage,artefactProps.URL)
      
    osChecker.checkAndCreateDir(os.path.split(batPath)[0])
    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])
    
    execURL = AVIDUrlLocater.getExecutableURL(self._session, "matlab", self._matlab)
    
    content = '"' + execURL + '" -wait -nodisplay -nosplash -nodesktop -r "'
           
    content += "BATmask( '"+lungPath+"', '" + thoraxPath+"', '" +resultPath+"'); exit;"
    
    with open(batPath, "w") as outputFile:
      outputFile.write(content)
      outputFile.close()
      
    return batPath      


class BATMaskBatchAction(BatchActionBase):    
  '''Batch action that uses the BAT BATMask matlab script.
     It will combine all given data of case/instance. The data will be sorted
     by timepoint.'''
  
  def __init__(self,  lungSelector, thoraxSelector, scriptDirectory, actionTag = "BATMask", alwaysDo = False,
               session = None, additionalActionProps = None, matlab = os.path.join("matlab","matlab.exe"), scheduler = SimpleScheduler()):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._lung = lungSelector.getSelection(self._session.inData)
    self._thorax = thoraxSelector.getSelection(self._session.inData)
    self._matlab = matlab
    self._scriptDirectory = scriptDirectory

      
  def _generateActions(self):
    #filter only type result. Other artefact types are not interesting
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)
    
    lung = self.ensureValidArtefacts(self._lung, resultSelector, "BATMask lung inputs")
    thorax = self.ensureValidArtefacts(self._thorax, resultSelector, "BATMask thorax inputs")
        
    thoraxLinker = CaseLinker()
    actions = list()

    for (pos,lungImage) in enumerate(lung):
      linkedThoraxes = thoraxLinker.getLinkedSelection(pos,lung,thorax)
      if len(linkedThoraxes) == 0:
        linkedThoraxes = [None]
        
      for lt in linkedThoraxes:
        action = BATMaskAction(lungImage, lt, self._scriptDirectory,
                              self._actionTag,
                              alwaysDo = self._alwaysDo,
                              session = self._session,
                              additionalActionProps = self._additionalActionProps,
                              matlab =self._matlab)
        actions.append(action)
              
    return actions
