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

class FFMapsAction(CLIActionBase):
  '''Class that wraps the single action for Matlab script FFMaps.'''

  def __init__(self, waterImage, fatImage, scriptDirectory,
               actionTag = "FFMaps", alwaysDo = False,
               session = None, additionalActionProps = None, matlab = os.path.join("matlab","matlab.exe")):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, scriptDirectory)
    self._addInputArtefacts(waterImage=waterImage, fatImage=fatImage)
     
    self._waterImage = waterImage
    self._fatImage = fatImage
    
    self._matlab = matlab
    
    self._coolstartID = artefactHelper.getArtefactProperty(waterImage, "coolstartID")
    self._coolendID = artefactHelper.getArtefactProperty(waterImage, "coolendID")
    self._targetID = artefactHelper.getArtefactProperty(waterImage, "targetID")
    
  def _generateName(self):
    name = "FFMap_"+str(artefactHelper.getArtefactProperty(self._waterImage,artefactProps.ACTIONTAG))+"_with_"+str(artefactHelper.getArtefactProperty(self._fatImage,artefactProps.ACTIONTAG))
    return name
   
  def _indicateOutputs(self):
    
    name = self.instanceName
                  
    self._batchArtefact = self.generateArtefact(self._waterImage)
    self._batchArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_MISC
    self._batchArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_BAT

    path = artefactHelper.generateArtefactPath(self._session, self._batchArtefact)
    batName = name + "." + str(artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.ID)) + ".bat"
    batName = os.path.join(path, batName)
    
    self._batchArtefact[artefactProps.URL] = batName
    
    self._resultArtefact = self.generateArtefact(self._batchArtefact)
    self._resultArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._resultArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_ITK
    self._resultArtefact[artefactProps.OBJECTIVE] = "complete"
    
    path = artefactHelper.generateArtefactPath(self._session, self._resultArtefact)
    resName = name + "_complete." + str(artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.ID)) + os.extsep + "nrrd"
    resName = os.path.join(path, resName)
    
    self._resultArtefact[artefactProps.URL] = resName
    
    self._resultCoolingArtefact = self.generateArtefact(self._batchArtefact)
    self._resultCoolingArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._resultCoolingArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_ITK
    self._resultCoolingArtefact[artefactProps.OBJECTIVE] = "cooling"
    
    resName = name + "_cooling." + str(artefactHelper.getArtefactProperty(self._resultCoolingArtefact,artefactProps.ID)) + os.extsep + "nrrd"
    resName = os.path.join(path, resName)
    
    self._resultCoolingArtefact[artefactProps.URL] = resName    

    self._resultFatArtefact = self.generateArtefact(self._batchArtefact)
    self._resultFatArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._resultFatArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_ITK
    self._resultFatArtefact[artefactProps.OBJECTIVE] = "fat"
    
    resName = name + "_fat." + str(artefactHelper.getArtefactProperty(self._resultFatArtefact,artefactProps.ID)) + os.extsep + "nrrd"
    resName = os.path.join(path, resName)
    
    self._resultFatArtefact[artefactProps.URL] = resName    

    self._resultWaterArtefact = self.generateArtefact(self._batchArtefact)
    self._resultWaterArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._resultWaterArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_ITK
    self._resultWaterArtefact[artefactProps.OBJECTIVE] = "fat"
    
    resName = name + "_water." + str(artefactHelper.getArtefactProperty(self._resultWaterArtefact,artefactProps.ID)) + os.extsep + "nrrd"
    resName = os.path.join(path, resName)
    
    self._resultWaterArtefact[artefactProps.URL] = resName    
    
    return [self._batchArtefact, self._resultArtefact, self._resultCoolingArtefact, self._resultWaterArtefact, self._resultFatArtefact]

      
  def _prepareCLIExecution(self):
    
    batPath = artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.URL)
    resultPath = artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.URL)
    resultCoolingPath = artefactHelper.getArtefactProperty(self._resultCoolingArtefact,artefactProps.URL)
    resultWaterPath = artefactHelper.getArtefactProperty(self._resultWaterArtefact,artefactProps.URL)
    resultFatPath = artefactHelper.getArtefactProperty(self._resultFatArtefact,artefactProps.URL)
    waterPath = artefactHelper.getArtefactProperty(self._waterImage,artefactProps.URL)
    fatPath = artefactHelper.getArtefactProperty(self._fatImage,artefactProps.URL)
      
    osChecker.checkAndCreateDir(os.path.split(batPath)[0])
    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])
    
    execURL = AVIDUrlLocater.getExecutableURL(self._session, "matlab", self._matlab)
    
    content = '"' + execURL + '" -wait -nodisplay -nosplash -nodesktop -r "'
           
    content += "FFMaps( " + str(self._targetID) + ", " +str(self._coolstartID)+ ", "+str(self._coolendID)+ ", '"+waterPath+"', '" + fatPath+"', '" +resultWaterPath+"', '" +resultFatPath+"', '" +resultPath+"', '" +resultCoolingPath+"'); exit;"
    
    with open(batPath, "w") as outputFile:
      outputFile.write(content)
      outputFile.close()
      
    return batPath      


class FFMapsBatchAction(BatchActionBase):    
  '''Batch action that uses the BAT FFMaps matlab script.
     It will combine all given data of case/instance. The data will be sorted
     by timepoint.'''
  
  def __init__(self,  waterSelector, fatSelector, scriptDirectory, actionTag = "FFMaps", alwaysDo = False,
               session = None, additionalActionProps = None, matlab = os.path.join("matlab","matlab.exe"), scheduler = SimpleScheduler()):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._water = waterSelector.getSelection(self._session.inData)
    self._fat = fatSelector.getSelection(self._session.inData)
    self._matlab = matlab
    self._scriptDirectory = scriptDirectory

      
  def _generateActions(self):
    #filter only type result. Other artefact types are not interesting
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)
    
    water = self.ensureRelevantArtefacts(self._water, resultSelector, "FFMaps water inputs")
    fat = self.ensureRelevantArtefacts(self._fat, resultSelector, "FFMaps fat inputs")
        
    fatLinker = CaseInstanceLinker()
    actions = list()

    for (pos,waterImage) in enumerate(water):
      linkedFat = fatLinker.getLinkedSelection(pos,water,fat)
      if len(linkedFat) == 0:
        linkedFat = [None]
        
      for lf in linkedFat:
        action = FFMapsAction(waterImage, lf, self._scriptDirectory,
                              self._actionTag,
                              alwaysDo = self._alwaysDo,
                              session = self._session,
                              additionalActionProps = self._additionalActionProps,
                              matlab =self._matlab)
        actions.append(action)
              
    return actions
