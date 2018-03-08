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

from builtins import str
import os
import logging
import re

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper

from avid.common import osChecker, AVIDUrlLocater
from . import BatchActionBase
from .cliActionBase import CLIActionBase
from avid.linkers import CaseLinker
from avid.selectors import TypeSelector
from .simpleScheduler import SimpleScheduler
from .doseMap import _getArtefactLoadStyle
import avid.externals.virtuos as virtuos
from avid.linkers.caseInstanceLinker import CaseInstanceLinker

logger = logging.getLogger(__name__)

class DoseStatAction(CLIActionBase):
  '''Class that wraps the single action for the tool doseMap.'''

  def __init__(self, inputDose, structSet, structName, computeDVH=True,
               actionTag = "DoseStat", alwaysDo = False, session = None,
               additionalActionProps = None, actionConfig = None, propInheritanceDict = None):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig = actionConfig, propInheritanceDict = propInheritanceDict)
    self._addInputArtefacts(inputDose=inputDose, structSet=structSet)
    self._inputDose = inputDose
    self._structSet = structSet
    self._structName = structName
    self._computeDVH = computeDVH
       
    cwd = os.path.dirname(AVIDUrlLocater.getExecutableURL(self._session, "DoseTool", actionConfig))
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

    self._resultArtefact = self.generateArtefact(self._inputDose,
                                                 userDefinedProps={artefactProps.TYPE:artefactProps.TYPE_VALUE_RESULT,
                                                                   artefactProps.FORMAT: artefactProps.FORMAT_VALUE_RTTB_STATS_XML,
                                                                   artefactProps.OBJECTIVE: self._structName},
                                                 urlHumanPrefix=self.instanceName,
                                                 urlExtension='xml')

    if self._computeDVH is True:
      name = name.replace("doseStat", "cumDVH")
      self._resultDVHArtefact = self.generateArtefact(self._inputDose,
                                                 userDefinedProps={artefactProps.TYPE:artefactProps.TYPE_VALUE_RESULT,
                                                                   artefactProps.FORMAT: artefactProps.FORMAT_VALUE_RTTB_CUM_DVH_XML,
                                                                   artefactProps.OBJECTIVE: self._structName},
                                                 urlHumanPrefix=name,
                                                 urlExtension='xml')
      return [self._resultArtefact, self._resultDVHArtefact]
    else:
      return [self._resultArtefact]
 
                
  def _prepareCLIExecution(self):
    
    resultPath = artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.URL)
    inputPath = artefactHelper.getArtefactProperty(self._inputDose,artefactProps.URL)
    structPath = artefactHelper.getArtefactProperty(self._structSet,artefactProps.URL)
    
    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])
    
    execURL = AVIDUrlLocater.getExecutableURL(self._session, "DoseTool", self._actionConfig)
    
    content = '"' + execURL + '"' + ' --doseFile "' + inputPath + '" --structFile "' + structPath + '" --doseStatistics "' + resultPath + '"'

    if self._computeDVH is True:
      resultDVHPath = artefactHelper.getArtefactProperty(self._resultDVHArtefact, artefactProps.URL)
      content += ' --DVH "' + resultDVHPath + '"'

    content += ' --structName "'+self._getStructPattern()+'"'
      
    content += ' --doseLoadStyle ' + _getArtefactLoadStyle(self._inputDose)
    content += ' --structLoadStyle ' + _getStructLoadStyle(self._structSet)
    
    return content
  
  
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
               structLinker = CaseLinker()+CaseInstanceLinker(), computeDVH=True,
               actionTag = "doseStat", alwaysDo = False,
               session = None, additionalActionProps = None, scheduler = SimpleScheduler(), **singleActionParameters):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._inputDoses = inputSelector.getSelection(self._session.artefacts)
    self._structSets = structSetSelector.getSelection(self._session.artefacts)

    self._structLinker = structLinker
    self._structNames = structNames
    self._singleActionParameters = singleActionParameters

    self._computeDVH = computeDVH

      
  def _generateActions(self):
    #filter only type result. Other artefact types are not interesting
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)
    
    inputs = self.ensureRelevantArtefacts(self._inputDoses, resultSelector, "doseStat doses")
    struct = self.ensureRelevantArtefacts(self._structSets, resultSelector, "doseStat structSets")
       
    actions = list()
    
    for (pos,inputDose) in enumerate(inputs):
      linkedStructs = self._structLinker.getLinkedSelection(pos,inputs,struct)
      if len(linkedStructs)==0:
        logger.warning("No linked structs found for dose. Skipped dose statistics. Dose: %s", inputDose)
        
      for ls in linkedStructs:
        for name in self._structNames:
          action = DoseStatAction(inputDose, ls, name, self._computeDVH,
                              self._actionTag, alwaysDo = self._alwaysDo,
                              session = self._session,
                              additionalActionProps = self._additionalActionProps,
                              **self._singleActionParameters)
          actions.append(action)
    
    return actions