import os
import logging
import re

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper

from avid.common import osChecker, AVIDUrlLocater
from . import BatchActionBase
from cliActionBase import CLIActionBase
from avid.linkers import CaseLinker
from avid.selectors import TypeSelector
from simpleScheduler import SimpleScheduler
from doseMap import _getArtefactLoadStyle
import avid.externals.virtuos as virtuos
from avid.linkers.caseInstanceLinker import CaseInstanceLinker

logger = logging.getLogger(__name__)

class DoseStatAction(CLIActionBase):
  '''Class that wraps the single action for the tool doseMap.'''

  def __init__(self, inputDose, structSet, structName,
               actionTag = "DoseStat", alwaysDo = False, session = None,
               additionalActionProps = None, actionConfig = None):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig)
    self._addInputArtefacts(inputDose=inputDose, structSet=structSet)
    self._inputDose = inputDose
    self._structSet = structSet
    self._structName = structName
       
    cwd = os.path.dirname(AVIDUrlLocater.getExecutableURL(self._session, "DoseStats", actionConfig))
    self._cwd = cwd    
    
  def _generateName(self):
    name = "doseStat_"+artefactHelper.ensureValidPath(str(self._structName))

    name += "__"+str(artefactHelper.getArtefactProperty(self._inputDose,artefactProps.ACTIONTAG))\
            +"_#"+str(artefactHelper.getArtefactProperty(self._inputDose,artefactProps.TIMEPOINT))

    name += "__"+str(artefactHelper.getArtefactProperty(self._structSet,artefactProps.ACTIONTAG))\
              +"_#"+str(artefactHelper.getArtefactProperty(self._structSet,artefactProps.TIMEPOINT))

    return name

   
  def _indicateOutputs(self):    
    name = self.instanceName
                    
    self._batchArtefact = self.generateArtefact(self._inputDose)
    self._batchArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_MISC
    self._batchArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_BAT
    self._batchArtefact[artefactProps.OBJECTIVE]= self._structName

    path = artefactHelper.generateArtefactPath(self._session, self._batchArtefact)
    batName = name + "." + str(artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.ID)) + os.extsep + "bat"
    batName = os.path.join(path, batName)
    
    self._batchArtefact[artefactProps.URL] = batName
    
    self._resultArtefact = self.generateArtefact(self._batchArtefact)
    self._resultArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._resultArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_RTTB_STATS_XML
    self._resultArtefact[artefactProps.OBJECTIVE]= self._structName
    
    path = artefactHelper.generateArtefactPath(self._session, self._resultArtefact)
    resName = name + "." + str(artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.ID)) + os.extsep + "xml"
    resName = os.path.join(path, resName)
    
    self._resultArtefact[artefactProps.URL] = resName

    self._resultDVHArtefact = self.generateArtefact(self._batchArtefact)
    self._resultDVHArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._resultDVHArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_RTTB_CUM_DVH_XML
    self._resultDVHArtefact[artefactProps.OBJECTIVE]= self._structName

    name = name.replace("doseStat", "cumDVH")
    path = artefactHelper.generateArtefactPath(self._session, self._resultDVHArtefact)
    resDVHName = name + "." + str(artefactHelper.getArtefactProperty(self._resultDVHArtefact,artefactProps.ID)) + os.extsep + "xml"
    resDVHName = os.path.join(path, resDVHName)

    self._resultDVHArtefact[artefactProps.URL] = resDVHName

    return [self._batchArtefact, self._resultArtefact, self._resultDVHArtefact]
 
                
  def _prepareCLIExecution(self):
    
    batPath = artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.URL)
    resultPath = artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.URL)
    resultDVHPath = artefactHelper.getArtefactProperty(self._resultDVHArtefact,artefactProps.URL)
    inputPath = artefactHelper.getArtefactProperty(self._inputDose,artefactProps.URL)
    structPath = artefactHelper.getArtefactProperty(self._structSet,artefactProps.URL)
    
    osChecker.checkAndCreateDir(os.path.split(batPath)[0])
    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])
    
    execURL = AVIDUrlLocater.getExecutableURL(self._session, "DoseStats", self._actionConfig)
    
    content = '"' + execURL + '"' + ' -d "' + inputPath + '" -s "' + structPath + '" --doseStatistics "' + resultPath + '"'

    content += ' --DVH "' + resultDVHPath + '"'

    content += ' -n "'+self._getStructPattern()+'"'
      
    content += ' --doseLoadStyle ' + _getArtefactLoadStyle(self._inputDose)
    content += ' --structLoadStyle ' + _getStructLoadStyle(self._structSet)
    
    with open(batPath, "w") as outputFile:
      outputFile.write(content)
      outputFile.close()
      
    return batPath      
  
  
  def _getStructPattern(self):
    aFormat = artefactHelper.getArtefactProperty(self._structSet,artefactProps.FORMAT)
    pattern = self._structName
    if not aFormat == artefactProps.FORMAT_VALUE_ITK:
      if self._session.hasStructurePattern(self._structName):
        pattern = self._session.structureDefinitions[self._structName]
      else:
        #we stay with the name, but be sure that it is a valid regex. because it
        #is expected by the doseTool
        pattern = re.escape(pattern)
    
    return pattern
    

def _getStructLoadStyle(structArtefact):
  'deduce the load style parameter for an artefact that should be input'
  aPath = artefactHelper.getArtefactProperty(structArtefact,artefactProps.URL)
  aFormat = artefactHelper.getArtefactProperty(structArtefact,artefactProps.FORMAT)
  
  result = ""
  
  if aFormat == artefactProps.FORMAT_VALUE_ITK:
    result = aFormat
  elif aFormat == artefactProps.FORMAT_VALUE_DCM:
    result = "dicom"
  elif aFormat == artefactProps.FORMAT_VALUE_HELAX_DCM:
    result = "helax"
  elif aFormat == artefactProps.FORMAT_VALUE_VIRTUOS:
    result = "virtuos"
    ctxPath = virtuos.stripFileExtensions(aPath)
    ctxPath = ctxPath + os.extsep+"ctx"
    if not os.path.isfile(ctxPath):
      ctxPath = ctxPath + os.extsep+"gz"
      if not os.path.isfile(ctxPath):
        msg = "Cannot calculate dose statistic. Virtuos cube for use struct file not faund. Struct file: "+aPath
        logger.error(msg)
        raise RuntimeError(msg)
          
    result = result + ' "' + ctxPath + '"'
  else:
    logger.info("No load style known for artefact format: %s", aFormat)
    
  return result


class DoseStatBatchAction(BatchActionBase):    
  '''Base class for action objects that are used together with selectors and
    should therefore able to process a batch of SingleActionBased actions.'''
  
  def __init__(self,  inputSelector, structSetSelector, structNames,
               structLinker = CaseLinker()+CaseInstanceLinker(), 
               actionTag = "doseStat", alwaysDo = False,
               session = None, additionalActionProps = None, actionConfig = None, scheduler = SimpleScheduler()):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._inputDoses = inputSelector.getSelection(self._session.inData)
    self._structSets = structSetSelector.getSelection(self._session.inData)

    self._structLinker = structLinker
    self._structNames = structNames
    self._actionConfig = actionConfig  

      
  def _generateActions(self):
    #filter only type result. Other artefact types are not interesting
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)
    
    inputs = self.ensureValidArtefacts(self._inputDoses, resultSelector, "doseStat doses")
    struct = self.ensureValidArtefacts(self._structSets, resultSelector, "doseStat structSets")
       
    actions = list()
    
    for (pos,inputDose) in enumerate(inputs):
      linkedStructs = self._structLinker.getLinkedSelection(pos,inputs,struct)
      if len(linkedStructs)==0:
        logger.warning("No linked structs found for dose. Skipped dose statistics. Dose: %s", inputDose)
        
      for ls in linkedStructs:
        for name in self._structNames:
          action = DoseStatAction(inputDose, ls, name,
                              self._actionTag, alwaysDo = self._alwaysDo,
                              session = self._session,
                              additionalActionProps = self._additionalActionProps,
                              actionConfig =self._actionConfig)
          actions.append(action)
    
    return actions