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

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper

from avid.common import osChecker, AVIDUrlLocater
from avid.actions import BatchActionBase
from avid.actions.cliActionBase import CLIActionBase
from avid.selectors import TypeSelector
from avid.actions.simpleScheduler import SimpleScheduler
from avid.linkers.caseInstanceLinker import CaseInstanceLinker

logger = logging.getLogger(__name__)

class BATCriteriaAction(CLIActionBase):
  '''Class that wraps the single action for Matlab script BATCriteria.'''

  def __init__(self, ffImage, maskImage, slopeImage, scriptDirectory,
               actionTag = "BATCriteria", alwaysDo = False,
               session = None, additionalActionProps = None, matlab = os.path.join("matlab","matlab.exe")):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, scriptDirectory)
    self._addInputArtefacts(ffImage=ffImage, maskImage=maskImage)
     
    self._ffImage = ffImage
    self._maskImage = maskImage
    self._slopeImage = slopeImage
    
    self._matlab = matlab
    
    self._coolstartID = artefactHelper.getArtefactProperty(ffImage, "coolstartID")
    self._coolendID = artefactHelper.getArtefactProperty(ffImage, "coolendID")
    self._cooltime = int(self._coolendID) - int(self._coolstartID)
       
  def _generateName(self):
    name = "BATCriteria_"+str(artefactHelper.getArtefactProperty(self._ffImage,artefactProps.ACTIONTAG))+"_by_"+str(artefactHelper.getArtefactProperty(self._maskImage,artefactProps.ACTIONTAG))+"_+_"+str(artefactHelper.getArtefactProperty(self._slopeImage,artefactProps.ACTIONTAG))
    return name
   
  def _indicateOutputs(self):
    
    name = self.instanceName
                  
    self._batchArtefact = self.generateArtefact(self._ffImage)
    self._batchArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_MISC
    self._batchArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_BAT

    path = artefactHelper.generateArtefactPath(self._session, self._batchArtefact)
    batName = name + "." + str(artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.ID)) + os.extsep + "bat"
    batName = os.path.join(path, batName)
    
    self._batchArtefact[artefactProps.URL] = batName
    
    self._resultArtefact = self.generateArtefact(self._batchArtefact)
    self._resultArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._resultArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_ITK
    self._resultArtefact[artefactProps.OBJECTIVE] = "median"
    
    path = artefactHelper.generateArtefactPath(self._session, self._resultArtefact)
    resName = name + "_median." + str(artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.ID)) + os.extsep + "nrrd"
    resName = os.path.join(path, resName)
    
    self._resultArtefact[artefactProps.URL] = resName
    
    self._resultLogicalArtefact = self.generateArtefact(self._batchArtefact)
    self._resultLogicalArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._resultLogicalArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_ITK
    self._resultLogicalArtefact[artefactProps.OBJECTIVE] = "logical"
    
    resName = name + "_logical." + str(artefactHelper.getArtefactProperty(self._resultLogicalArtefact,artefactProps.ID)) + os.extsep + "nrrd"
    resName = os.path.join(path, resName)
    
    self._resultLogicalArtefact[artefactProps.URL] = resName    
   
    return [self._batchArtefact, self._resultArtefact, self._resultLogicalArtefact]

      
  def _prepareCLIExecution(self):
    
    batPath = artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.URL)
    resultPath = artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.URL)
    resultLogicalPath = artefactHelper.getArtefactProperty(self._resultLogicalArtefact,artefactProps.URL)
    ffPath = artefactHelper.getArtefactProperty(self._ffImage,artefactProps.URL)
    maskPath = artefactHelper.getArtefactProperty(self._maskImage,artefactProps.URL)
    slopePath = artefactHelper.getArtefactProperty(self._slopeImage,artefactProps.URL)
      
    osChecker.checkAndCreateDir(os.path.split(batPath)[0])
    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])
    
    execURL = AVIDUrlLocater.getExecutableURL(self._session, "matlab", self._matlab)
    
    content = '"' + execURL + '" -wait -nodisplay -nosplash -nodesktop -r "'
           
    content += "BATCriteria( " + str(self._cooltime) + ", " +str(self._coolstartID)+ ", "+str(self._coolendID)+ ", '"+ffPath+"', '" + maskPath+"', '" +slopePath+"', '" +resultPath+"', '" +resultLogicalPath+"'); exit;"
    
    with open(batPath, "w") as outputFile:
      outputFile.write(content)
      outputFile.close()
      
    return batPath      


class BATCriteriaBatchAction(BatchActionBase):    
  '''Batch action that uses the BAT BATCriteria matlab script.'''
  
  def __init__(self,  ffSelector, maskSelector, slopeSelector, scriptDirectory, actionTag = "BATCriteria", alwaysDo = False,
               session = None, additionalActionProps = None, matlab = os.path.join("matlab","matlab.exe"), scheduler = SimpleScheduler()):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._ff = ffSelector.getSelection(self._session.inData)
    self._mask = maskSelector.getSelection(self._session.inData)
    self._slope = slopeSelector.getSelection(self._session.inData)
    self._matlab = matlab
    self._scriptDirectory = scriptDirectory

      
  def _generateActions(self):
    #filter only type result. Other artefact types are not interesting
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)
    
    ffs = self.ensureRelevantArtefacts(self._ff, resultSelector, "BATCriteria ff inputs")
    masks = self.ensureRelevantArtefacts(self._mask, resultSelector, "BATCriteria mask inputs")
    slopes = self.ensureRelevantArtefacts(self._slope, resultSelector, "BATCriteria mask inputs")
        
    linker = CaseInstanceLinker()
    actions = list()

    for (pos,ffImage) in enumerate(ffs):
      linkedMasks = linker.getLinkedSelection(pos,ffs,masks)
        
      linkedSlopes = linker.getLinkedSelection(pos,ffs,slopes)

      for lm in linkedMasks:
        for ls in linkedSlopes:
          action = BATCriteriaAction(ffImage, lm, ls, self._scriptDirectory,
                              self._actionTag,
                              alwaysDo = self._alwaysDo,
                              session = self._session,
                              additionalActionProps = self._additionalActionProps,
                              matlab =self._matlab)
          actions.append(action)
              
    return actions
