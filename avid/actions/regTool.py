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


class regToolAction(CLIActionBase):
  '''Class that wrapps the single action for the tool mapR.'''

  def __init__(self, targetImage, movingImage, configTemplate, targetMask = None,  movingMask = None, 
               targetIsReference = True, actionTag = "regTool", alwaysDo = False,
               session = None, additionalActionProps = None, actionConfig = None, propInheritanceDict = dict()):
       
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig = actionConfig, propInheritanceDict = propInheritanceDict)
    self._addInputArtefacts(targetImage = targetImage, movingImage = movingImage, targetMask = targetMask, movingMask = movingMask)

    self._targetImage = targetImage
    self._targetMask = targetMask
    self._movingImage = movingImage
    self._movingMask = movingMask
    self._configTemplate = configTemplate
    self._targetIsReference = targetIsReference

    cwd = os.path.dirname(AVIDUrlLocater.getExecutableURL(self._session, "regTool", actionConfig))
    self._cwd = cwd
  
  
  def _generateName(self):
    name = "reg_"+str(artefactHelper.getArtefactProperty(self._movingImage,artefactProps.ACTIONTAG))\
            +"_#"+str(artefactHelper.getArtefactProperty(self._movingImage,artefactProps.TIMEPOINT))

    if self._movingMask is not None:
      name += "_"+str(artefactHelper.getArtefactProperty(self._targetImage,artefactProps.ACTIONTAG))

    name += "_to_"+str(artefactHelper.getArtefactProperty(self._targetImage,artefactProps.ACTIONTAG))\
            +"_#"+str(artefactHelper.getArtefactProperty(self._targetImage,artefactProps.TIMEPOINT))

    if self._targetMask is not None:
      name += "_"+str(artefactHelper.getArtefactProperty(self._targetImage,artefactProps.ACTIONTAG))
      
    return name
    
  def _indicateOutputs(self):
    
    artefactRef = self._targetImage
    if not self._targetIsReference:
      artefactRef = self._movingImage
    
    name = self._generateName()
    
    #Specify batch artefact                
    self._batchArtefact = self.generateArtefact(artefactRef)
    self._batchArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_MISC
    self._batchArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_BAT

    path = artefactHelper.generateArtefactPath(self._session, self._batchArtefact)
    batName = name + "." + str(artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.ID)) + os.extsep + "bat"
    batName = os.path.join(path, batName)
    
    self._batchArtefact[artefactProps.URL] = batName
    
    #Specify config artefact                
    self._configArtefact = self.generateArtefact(self._batchArtefact)
    self._configArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_CONFIG
    self._configArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_AVIDXML
    
    path = artefactHelper.generateArtefactPath(self._session, self._configArtefact)
    resName = name + "." + str(artefactHelper.getArtefactProperty(self._configArtefact,artefactProps.ID)) + os.extsep + "reg.xml"
    resName = os.path.join(path, resName)
    
    self._configArtefact[artefactProps.URL] = resName    
    
    #Specify result artefact                
    self._resultArtefact = self.generateArtefact(self._batchArtefact)
    self._resultArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._resultArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_MATCHPOINT
    
    path = artefactHelper.generateArtefactPath(self._session, self._resultArtefact)
    resName = name + "." + str(artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.ID)) + os.extsep + "mapr"
    resName = os.path.join(path, resName)
    
    self._resultArtefact[artefactProps.URL] = resName

    return [self._batchArtefact, self._configArtefact, self._resultArtefact]


  def _createHeader(self, root):
    ''' Header Info'''
    name = self._generateName()
    Names = root.findall("Name")
    Names[0].text = str(self._actionTag)+"_"+name

    
  def _createImageParameters(self, root, paramName, image): 
    imagePath = artefactHelper.getArtefactProperty(image,artefactProps.URL)
    imageFormat = artefactHelper.getArtefactProperty(image,artefactProps.FORMAT)

    nodes = root.findall(".//Parameters/Parameter[@Name='"+paramName+"']") 
    for node in nodes:
      fileParam = node.find("Value[@Name='"+Tag.XML_File+"']")
      if fileParam is not None:
        fileParam.text = imagePath
      fileParam = node.find("Value[@Name='"+Tag.XML_Type+"']")
      if fileParam is not None:
        if imageFormat == artefactProps.FORMAT_VALUE_ITK:
          fileParam.text = "generic"
        else:
          fileParam.text = imageFormat

        
  def _createMaskParameters(self, root, paramName, mask): 
    maskPath = artefactHelper.getArtefactProperty(mask,artefactProps.URL)
    maskFormat = artefactHelper.getArtefactProperty(mask,artefactProps.FORMAT)

    nodes = root.findall(".//Parameters/Parameter[@Name='"+paramName+"']") 
    for node in nodes:
      if maskPath is None:
        root.remove(node)
        logger.info('RegTool config template has mask entry "%s", but no mask artefact passed to action. Mask/Entry is ignored.', paramName)
      else:
        fileParam = node.find("Value[@Name='"+Tag.XML_File+"']")
        if fileParam is not None:
          fileParam.text = maskPath
        fileParam = node.find("Value[@Name='"+Tag.XML_Type+"']")
        if fileParam is not None:
          fileParam.text = maskFormat        
 
     
  def _createResultInfoParameters(self, root):
    ''' create all parameters necessary '''
    resultPath = artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.URL)
    resultDir, resultFile = os.path.split(resultPath)
    
    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])

    nodes = root.findall(".//Parameters/Parameter[@Name='"+Tag.XML_ResultInfo+"']") 
    for node in nodes:
      param = node.find("Value[@Name='"+Tag.XML_ResultFilePath+"']")
      if param is not None:
        param.text = resultDir
      param = node.find("Value[@Name='"+Tag.XML_ResultFileName+"']")
      if param is not None:
        param.text = os.path.splitext(resultFile)[0]
      param = node.find("Value[@Name='"+Tag.XML_ResultObjectPath+"']")
      if param is not None:
        param.text = resultDir
      param = node.find("Value[@Name='"+Tag.XML_ResultObject+"']")
      if param is not None:
        param.text = resultFile       


  def _generateConfigFile(self, configPath):

    try:
        with open(configPath, 'w', 0) as outputFileHandle:
          tree = ElementTree()
          try:
            datasource = open(self._configTemplate)
          except SyntaxError:
            logger.error("Config file template couldn't get loaded")
            raise
        
          tree.parse(datasource)
          root = tree.getroot()
          self._createHeader(root)
          self._createImageParameters(root, Tag.XML_TargetImage, self._targetImage)
          self._createMaskParameters(root, Tag.XML_TargetMask, self._targetMask)
          self._createImageParameters(root, Tag.XML_MovingImage, self._movingImage)
          self._createMaskParameters(root, Tag.XML_MovingMask, self._movingMask)
          self._createResultInfoParameters(root)

          tree.write(outputFileHandle)
          datasource.close()  
          outputFileHandle.close()
    
        time.sleep(0.5) #pause a bit before continue. In some cases we could otherwise be faster with the call then the writing process.
    except:
      logger.error("Error generating config file: %s", configPath)
      raise
        
  def _prepareCLIExecution(self):
    
    batPath = artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.URL)
    configPath = artefactHelper.getArtefactProperty(self._configArtefact,artefactProps.URL)
    resultPath = artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.URL)
    
#    try:
    osChecker.checkAndCreateDir(os.path.split(batPath)[0])
#    except:
#      logger.error("Error for batPath.")
#      raise
      
#    try:
    osChecker.checkAndCreateDir(os.path.split(configPath)[0])
#    except:
#      logger.error("Error for configPath.")
#      raise

#    try:
    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])
#    except:
#      logger.error("Error for resultPath.")
#      raise
    
    try:
      self._generateConfigFile(configPath)
    except:
      logger.error("Error for _generateConfigFile.")
      raise
      
    try:
      execURL = AVIDUrlLocater.getExecutableURL(self._session, "regTool", self._actionConfig)
    
      content = '"' + execURL + '"' + ' "' + configPath + '"'
    except:
      logger.error("Error for getexecutable.")
      raise
    
    try:
      with open(batPath, "w") as outputFile:
        outputFile.write(content)
        outputFile.close()
    except:
      logger.error("Error for bat write.")
      raise
      
    return batPath      


class regToolBatchAction(BatchActionBase):    
  '''Action for batch processing of the regTool.'''
  
  def __init__(self,  targetSelector, movingSelector,
               targetMaskSelector = None, movingMaskSelector = None,
               movingLinker = CaseLinker(), targetMaskLinker = FractionLinker(), 
               movingMaskLinker = FractionLinker(), actionTag = "regTool", alwaysDo = False,
               session = None, additionalActionProps = None, scheduler = SimpleScheduler(),
               **singleActionParameters):
    
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._targetImages = targetSelector.getSelection(self._session.inData)
    self._targetMasks = list()
    if targetMaskSelector is not None:
      self._targetMasks = targetMaskSelector.getSelection(self._session.inData)

    self._movingImages = movingSelector.getSelection(self._session.inData)
    self._movingMasks = list()
    if movingMaskSelector is not None:
      self._movingMasks = movingMaskSelector.getSelection(self._session.inData)
    
    self._movingLinker = movingLinker
    self._targetMaskLinker = targetMaskLinker  
    self._movingMaskLinker = movingMaskLinker
    self._singleActionParameters = singleActionParameters

      
  def _generateActions(self):
    #filter only type result. Other artefact types are not interesting
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)
    
    targets = self.ensureValidArtefacts(self._targetImages, resultSelector, "regTool targets")
    movings = self.ensureValidArtefacts(self._movingImages, resultSelector, "regTool movings")
    targetMasks = self.ensureValidArtefacts(self._targetMasks, resultSelector, "regTool target masks")
    movingMasks = self.ensureValidArtefacts(self._movingMasks, resultSelector, "regTool moving masks")
      
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
            action = regToolAction(target, movingImage=lm, targetMask=ltm, movingMask=lmm,
                                   actionTag = self._actionTag,
                                   alwaysDo = self._alwaysDo, session = self._session,
                                   additionalActionProps = self._additionalActionProps,
                                   **self._singleActionParameters)
            actions.append(action)
    
    return actions
