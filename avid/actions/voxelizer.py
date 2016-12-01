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
import re

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper

from avid.common import osChecker, AVIDUrlLocater
from . import BatchActionBase
from cliActionBase import CLIActionBase
from avid.linkers import CaseLinker
from avid.selectors import TypeSelector
from simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)

class VoxelizerAction(CLIActionBase):
  '''Class that wraps the single action for the tool rttb VoxelizerTool.'''

  def __init__(self, structSet, referenceImage, structName,
               actionTag = "Voxelizer", allowIntersections = True,
               booleanMask = False, outputExt = 'nrrd', alwaysDo = False, session = None,
               additionalActionProps = None, actionConfig = None, propInheritanceDict = dict()):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig=actionConfig, propInheritanceDict = propInheritanceDict)
    self._addInputArtefacts(structSet = structSet, referenceImage = referenceImage)
    self._referenceImage = referenceImage
    self._structSet = structSet
    self._structName = structName
    self._outputExt = outputExt
    self._booleanMask = booleanMask
    self._allowIntersections = allowIntersections
    
    cwd = os.path.dirname(AVIDUrlLocater.getExecutableURL(self._session, "VoxelizerTool", actionConfig))
    self._cwd = cwd    
    
  def _generateName(self):
    name = "voxelize_"+artefactHelper.ensureValidPath(str(self._structName))

    name += "_in_"+str(artefactHelper.getArtefactProperty(self._structSet,artefactProps.ACTIONTAG))\
            +"_#"+str(artefactHelper.getArtefactProperty(self._structSet,artefactProps.TIMEPOINT))

    name += "_to_"+str(artefactHelper.getArtefactProperty(self._referenceImage,artefactProps.ACTIONTAG))\
              +"_#"+str(artefactHelper.getArtefactProperty(self._referenceImage,artefactProps.TIMEPOINT))

    return name

   
  def _indicateOutputs(self):    
    name = self.instanceName
                    
    self._batchArtefact = self.generateArtefact(self._structSet)
    self._batchArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_MISC
    self._batchArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_BAT
    self._batchArtefact[artefactProps.OBJECTIVE]= self._structName

    path = artefactHelper.generateArtefactPath(self._session, self._batchArtefact)
    batName = name + "." + str(artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.ID)) + os.extsep + "bat"
    batName = os.path.join(path, batName)
    
    self._batchArtefact[artefactProps.URL] = batName
    
    self._resultArtefact = self.generateArtefact(self._batchArtefact)
    self._resultArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._resultArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_ITK
    self._resultArtefact[artefactProps.OBJECTIVE]= self._structName
    
    path = artefactHelper.generateArtefactPath(self._session, self._resultArtefact)
    resName = name + "." + str(artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.ID)) + os.extsep + self._outputExt
    resName = os.path.join(path, resName)
    
    self._resultArtefact[artefactProps.URL] = resName

    return [self._batchArtefact, self._resultArtefact]
 
                
  def _prepareCLIExecution(self):
    
    batPath = artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.URL)
    resultPath = artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.URL)
    refPath = artefactHelper.getArtefactProperty(self._referenceImage,artefactProps.URL)
    structPath = artefactHelper.getArtefactProperty(self._structSet,artefactProps.URL)
    
    osChecker.checkAndCreateDir(os.path.split(batPath)[0])
    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])
    
    execURL = AVIDUrlLocater.getExecutableURL(self._session, "VoxelizerTool", self._actionConfig)
    
    content = '"' + execURL + '"' + ' -s "' + structPath + '" -r "' + refPath + '" -o "' + resultPath + '"'

    content += ' -y itk -a'

    if self._allowIntersections:
      content += ' -i'
      
    if self._booleanMask:
      content += ' -z'
      
    content += ' -e "'+self._getStructPattern()+'"'
      
    
    with open(batPath, "w") as outputFile:
      outputFile.write(content)
      outputFile.close()
      
    return batPath      
  
  
  def _getStructPattern(self):
    pattern = self._structName
    if self._session.hasStructurePattern(self._structName):
      pattern = self._session.structureDefinitions[self._structName]
    else:
      #we stay with the name, but be sure that it is a valid regex. because it
      #is expected by the doseTool
      pattern = re.escape(pattern)
    
    return pattern
    

class VoxelizerBatchAction(BatchActionBase):    
  '''Batch action for the voxelizer tool..'''
  
  def __init__(self, structSetSelector, referenceSelector, structNames = None,
               referenceLinker = CaseLinker(), 
               actionTag = "doseStat", alwaysDo = False,
               session = None, additionalActionProps = None, scheduler = SimpleScheduler(), **singleActionParameters):
    ''' Batch action for the voxelizer tool.
    @param structNames: List of the structures names that should be voxelized.
     If none is passed all structures defined in current session's structure
     definitions. 
    '''
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._references = referenceSelector.getSelection(self._session.inData)
    self._structSets = structSetSelector.getSelection(self._session.inData)

    self._refLinker = referenceLinker
    self._structNames = structNames
    if (self._structNames is None):
      self._structNames = self._session.structureDefinitions.keys()
    self._singleActionParameters = singleActionParameters

      
  def _generateActions(self):
    #filter only type result. Other artefact types are not interesting
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)
    
    refs = self.ensureValidArtefacts(self._references, resultSelector, "reference images")
    structs = self.ensureValidArtefacts(self._structSets, resultSelector, "doseStat structSets")
       
    actions = list()
    
    for (pos,struct) in enumerate(structs):
      linkedRefs = self._refLinker.getLinkedSelection(pos,structs, refs)
      if len(linkedRefs)==0:
        logger.warning("No linked references found for voxelization. Skipped voxelization. Struct: %s", struct)
        
      for lr in linkedRefs:
        for name in self._structNames:
          action = VoxelizerAction(struct, lr, name,
                              self._actionTag, alwaysDo = self._alwaysDo,
                              session = self._session,
                              additionalActionProps = self._additionalActionProps,
                              **self._singleActionParameters)
          actions.append(action)
    
    return actions