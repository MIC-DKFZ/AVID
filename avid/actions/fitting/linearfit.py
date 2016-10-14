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
               session = None, additionalActionProps = None, miniapp = os.path.join("GenericFittingMiniApp","GenericFittingMiniApp.exe")):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps)
    self._setCaseInstanceByArtefact(inputImage, maskImage)
     
    self._inputImage = inputImage
    self._maskImage = maskImage
    
    self._roibased = roibased
    
    self._miniapp = miniapp
    
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
    
    name = self.instanceName
                  
    self._batchArtefact = self.generateArtefact(self._inputImage)
    self._batchArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_MISC
    self._batchArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_BAT

    path = artefactHelper.generateArtefactPath(self._session, self._batchArtefact)
    batName = name + "." + str(artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.ID))+os.extsep+"bat"
    batName = os.path.join(path, batName)
       
    self._batchArtefact[artefactProps.URL] = batName
    
    outputTemplate = name + "." + str(artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.ID))
    
    self._resultSlopeArtefact = self.generateArtefact(self._batchArtefact)
    self._resultSlopeArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._resultSlopeArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_ITK
    self._resultSlopeArtefact[artefactProps.OBJECTIVE] = "slope"
    
    path = artefactHelper.generateArtefactPath(self._session, self._resultSlopeArtefact)
    resName = outputTemplate + "_slope"+os.extsep+"nrrd"
    resName = os.path.join(path, resName)
    
    self._resultSlopeArtefact[artefactProps.URL] = resName
    
    self._resultOffsetArtefact = self.generateArtefact(self._batchArtefact)
    self._resultOffsetArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._resultOffsetArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_ITK
    self._resultOffsetArtefact[artefactProps.OBJECTIVE] = "offset"
    
    resName = outputTemplate + "_offset"+os.extsep+"nrrd"
    resName = os.path.join(path, resName)
    
    self._resultOffsetArtefact[artefactProps.URL] = resName    

    self._outputTemplatePath = os.path.join(path, outputTemplate+os.extsep+"nrrd")
  
    return [self._batchArtefact, self._resultSlopeArtefact, self._resultOffsetArtefact]

      
  def _prepareCLIExecution(self):
    
    batPath = artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.URL)
    resultPath = artefactHelper.getArtefactProperty(self._resultSlopeArtefact,artefactProps.URL)
    inputPath = artefactHelper.getArtefactProperty(self._inputImage,artefactProps.URL)
    maskPath = artefactHelper.getArtefactProperty(self._maskImage,artefactProps.URL)
      
    osChecker.checkAndCreateDir(os.path.split(batPath)[0])
    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])
    
    execURL = AVIDUrlLocater.getExecutableURL(self._session, "GenericFittingMiniApp", self._miniapp)
    
    content = '"' + execURL + '" -f Linear -i "'+str(inputPath)+'" -o "'+ self._outputTemplatePath+'"'
    
    if maskPath is not None:
      content += ' -m "'+maskPath+'"'
      
    if self._roibased:
      content += "-r"
             
    with open(batPath, "w") as outputFile:
      outputFile.write(content)
      outputFile.close()
      
    return batPath      



class LinearFitBatchAction(BatchActionBase):    
  '''Batch action that uses the MITK GenericFittingMiniApp to make a linear fit.'''
  
  def __init__(self,  inputSelector, maskSelector, maskLinker = CaseLinker(), roibased = False, actionTag = "LinearFit", alwaysDo = False,
               session = None, additionalActionProps = None, miniapp = os.path.join("GenericFittingMiniApp","GenericFittingMiniApp.exe"), scheduler = SimpleScheduler()):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._inputs = inputSelector.getSelection(self._session.inData)
    self._masks = maskSelector.getSelection(self._session.inData)
    self._miniapp = miniapp
    self._maskLinker = maskLinker
    self._roibased = roibased

      
  def _generateActions(self):
    #filter only type result. Other artefact types are not interesting
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)
    
    inputs = self.ensureValidArtefacts(self._inputs, resultSelector, "4D inputs")
    masks = self.ensureValidArtefacts(self._masks, resultSelector, "Mask inputs")
        
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
