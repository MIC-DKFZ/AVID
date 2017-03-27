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
import shutil
import re

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper
import avid.externals.virtuos as virtuos

from avid.common import osChecker, AVIDUrlLocater
from avid.actions import BatchActionBase
from avid.actions.cliActionBase import CLIActionBase
from avid.linkers import FractionLinker
from avid.selectors import TypeSelector
from .simpleScheduler import SimpleScheduler


logger = logging.getLogger(__name__)
DEFAULT_PLAN_NR = "1"


class pdcAction(CLIActionBase):
  '''Class that wrapps the single action for the tool PDC++.'''

  def __init__(self, image, plan, struct, 
               actionTag = "pdc", executionBat = None, alwaysDo = False,
               session = None, additionalActionProps = None, actionConfig = None, propInheritanceDict = dict()):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig = actionConfig,
                           propInheritanceDict = propInheritanceDict)
    self._addInputArtefacts(image = image, plan = plan, struct = struct)

    self._image = image
    self._plan = plan
    self._struct = struct
    self._executionBat = executionBat
  
  def _generateName(self):
    name = "pdc_"+str(artefactHelper.getArtefactProperty(self._plan,artefactProps.ACTIONTAG))\
            +"_#"+str(artefactHelper.getArtefactProperty(self._plan,artefactProps.TIMEPOINT))

    name += "_on_"+str(artefactHelper.getArtefactProperty(self._image,artefactProps.ACTIONTAG))\
            +"_#"+str(artefactHelper.getArtefactProperty(self._image,artefactProps.TIMEPOINT))

    return name
    
  def _indicateOutputs(self):
    
    global DEFAULT_PLAN_NR
    artefactRef = self._image

    name = self._generateName()

    #Specify result dose artefact
    self._resultDoseArtefact = self.generateArtefact(artefactRef)
    self._resultDoseArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._resultDoseArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_VIRTUOS

    path = artefactHelper.generateArtefactPath(self._session, self._resultDoseArtefact)
    resultID = str(artefactHelper.getArtefactProperty(self._resultDoseArtefact,artefactProps.ID))
    resName = name + "." + resultID + "_"+ DEFAULT_PLAN_NR + os.extsep + "dos.gz"
    resName = os.path.join(path, resName)

    self._resultDoseArtefact[artefactProps.URL] = resName
        
    #Specify result plan artefact                
    self._resultPlanArtefact = self.generateArtefact(self._resultDoseArtefact)
    self._resultPlanArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._resultPlanArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_VIRTUOS_PLAN
    
    resName = virtuos.stripFileExtensions(resName) + os.extsep + "pln"  
    self._resultPlanArtefact[artefactProps.URL] = resName
    
    #Specify result head artefact                
    self._resultHeadArtefact = self.generateArtefact(self._resultDoseArtefact)
    self._resultHeadArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._resultHeadArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_VIRTUOS_HEAD
    
    resName = virtuos.stripFileExtensions(resName) + os.extsep + "hed"  
    self._resultHeadArtefact[artefactProps.URL] = resName
        
    #Specify batch artefact                
    self._batchArtefact = self.generateArtefact(artefactRef)
    self._batchArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_MISC
    self._batchArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_BAT

    path = artefactHelper.generateArtefactPath(self._session, self._batchArtefact)
    batName = name + "." + str(artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.ID)) + os.extsep + "bat"
    batName = os.path.join(path, batName)
    
    self._batchArtefact[artefactProps.URL] = batName
    
    #Specify cloned input artefact
    #cloning is necessary because pdc++ needs everything to be in one directory                
    #we are breaking with the normal naming conventions here to have
    #1) file names that can be handled by pdc++
    #2) same name for all input data
    #3) names that can be easily tracked by knowing the result name
    self._ownPlanArtefact = self.generateArtefact(self._resultDoseArtefact)
    self._ownPlanArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_MISC
    self._ownPlanArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_VIRTUOS_PLAN
    path = artefactHelper.generateArtefactPath(self._session, self._ownPlanArtefact)

    ownName = os.path.join(path, resultID + "_"+ DEFAULT_PLAN_NR + os.extsep + "pln")
    self._ownPlanArtefact[artefactProps.URL] = ownName    
    
    self._ownImageArtefact = self.generateArtefact(self._ownPlanArtefact)
    imgExt = virtuos.getFileExtensions(artefactHelper.getArtefactProperty(self._image,artefactProps.URL))
    ownName = os.path.join(path, resultID + imgExt)
    self._ownImageArtefact[artefactProps.URL] = ownName    

    self._ownHeadArtefact = self.generateArtefact(self._ownPlanArtefact)
    ownName = os.path.join(path, resultID + os.extsep + "hed")
    self._ownHeadArtefact[artefactProps.URL] = ownName    

    self._ownStructArtefact = self.generateArtefact(self._ownPlanArtefact)
    structExt = virtuos.getFileExtensions(artefactHelper.getArtefactProperty(self._struct,artefactProps.URL))
    ownName = os.path.join(path, resultID + structExt)
    self._ownStructArtefact[artefactProps.URL] = ownName    


    return [self._batchArtefact, self._ownImageArtefact,
            self._ownPlanArtefact, self._ownHeadArtefact,
            self._ownStructArtefact, self._resultDoseArtefact,
            self._resultHeadArtefact, self._resultPlanArtefact]


  def _copyOwnArtefacts(self):
    ownPlan = artefactHelper.getArtefactProperty(self._ownPlanArtefact,artefactProps.URL)
    ownImage = artefactHelper.getArtefactProperty(self._ownImageArtefact,artefactProps.URL)
    ownHead = artefactHelper.getArtefactProperty(self._ownHeadArtefact,artefactProps.URL)
    ownStruct = artefactHelper.getArtefactProperty(self._ownStructArtefact,artefactProps.URL)
    plan = artefactHelper.getArtefactProperty(self._plan,artefactProps.URL)
    image = artefactHelper.getArtefactProperty(self._image,artefactProps.URL)
    head = virtuos.stripFileExtensions(image)+ os.extsep + "hed"
    struct = artefactHelper.getArtefactProperty(self._struct,artefactProps.URL)
    
    logger.debug("Copy plan to '%s'", ownPlan)
    shutil.copy(plan, ownPlan)
    logger.debug("Copy image to '%s'", ownImage)
    shutil.copy(image, ownImage)
    logger.debug("Copy head to '%s'", ownHead)
    shutil.copy(head, ownHead)
    logger.debug("Copy struct to '%s'", ownStruct)
    shutil.copy(struct, ownStruct)


  def _copyResults(self):
    resDose = artefactHelper.getArtefactProperty(self._resultDoseArtefact,artefactProps.URL)
    baseName = virtuos.stripFileExtensions(resDose)
    resHead = baseName + os.extsep + "hed"
    resPlan = baseName + os.extsep + "pln"
    
    ownPlan = artefactHelper.getArtefactProperty(self._ownPlanArtefact,artefactProps.URL)
    baseName = virtuos.stripFileExtensions(ownPlan)
    ownHead = baseName + os.extsep + "hed"
    ownDose = baseName + os.extsep + "dos"
    if not os.path.isfile(ownDose):
      ownDose = ownDose + os.extsep + "gz"
      if not os.path.isfile(ownDose):
        logger.error("Error when copying results. Resulting dose does not exist where expected. Expected location: %s",ownDose)

    plan = artefactHelper.getArtefactProperty(self._plan,artefactProps.URL)
    self._correctPlan(plan, ownPlan)
      
    logger.debug("Copy plan to '%s'", resPlan)
    shutil.copy(ownPlan, resPlan)
    logger.debug("Copy dose to '%s'", resDose)
    shutil.copy(ownDose, resDose)
    logger.debug("Copy head to '%s'", resHead)
    shutil.copy(ownHead, resHead)

  def _correctPlan(self, inputFilename, outputFilename):

    try:
      planStr = virtuos.readFile(inputFilename)
      fractionNR = virtuos.getValueFromPlan(planStr, virtuos.KEY_NUM_FRACTIONS)
      prescribedDose = virtuos.getValueFromPlan(planStr, virtuos.KEY_PRESCRIBED_DOSE)

      newPlanStr = virtuos.setValueInPlan(planStr,virtuos.KEY_PRESCRIBED_DOSE,prescribedDose)
      newPlanStr = virtuos.setValueInPlan(newPlanStr,virtuos.KEY_NUM_FRACTIONS,fractionNR)

      virtuos.writeFile(outputFilename, newPlanStr)
    except:
      logger.warning("Unable to correct plan %s", str(inputFilename))
      raise

  def _prepareCLIExecution(self):
    ownPlan = artefactHelper.getArtefactProperty(self._ownPlanArtefact,artefactProps.URL)
    ownImage = os.path.split(artefactHelper.getArtefactProperty(self._ownImageArtefact,artefactProps.URL))[1]
    ownStruct = os.path.split(artefactHelper.getArtefactProperty(self._ownStructArtefact,artefactProps.URL))[1]
    resultPath = artefactHelper.getArtefactProperty(self._resultDoseArtefact,artefactProps.URL)
    batPath = artefactHelper.getArtefactProperty(self._batchArtefact,artefactProps.URL)
    inputPath = os.path.split(ownPlan)[0]

    execURL = AVIDUrlLocater.getExecutableURL(self._session, "pdc++", self._actionConfig)
    #It assumes that the exe is stored in root/bin/[exe]
    pdcRootPath = os.path.dirname(os.path.dirname(execURL)) 
    pdcDevicePath= os.path.join(os.path.dirname(pdcRootPath),"Resources", "TestData")
    
    osChecker.checkAndCreateDir(os.path.split(ownPlan)[0])
    osChecker.checkAndCreateDir(os.path.split(batPath)[0])
    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])

    self._copyOwnArtefacts()
    
    #TODO 2016-03-02: New PDC++ by precises seems to change its behaviour
    # drastically. In contrast to old version it now complaints if the values
    # aren't set. In earlier version the must not be set(!). Have to check back
    # on precisis regarding that matter/observe the behaviour in the future.
    #virtuos.resetPlanFile(ownPlan)
            
    patient = artefactHelper.getArtefactProperty(self._resultDoseArtefact,artefactProps.ID)
    global DEFAULT_PLAN_NR
    virtuos.generateBatchFile(batPath, self._executionBat, pdcRootPath, patient, ownImage, ownStruct, DEFAULT_PLAN_NR, inputPath, inputPath, pdcDevicePath)
          
    return batPath      


  def _addPlanProperties(self, planArtefact):
    '''reads special properties from the plan file referenced by the artefact
    and adds the properties to the artefact for other workflow parts.'''
    resultPath = artefactHelper.getArtefactProperty(planArtefact,artefactProps.URL)
    try:
      planStr = virtuos.readFile(resultPath)
      fractionNR = virtuos.getValueFromPlan(planStr, virtuos.KEY_NUM_FRACTIONS)
      prescribedDose = virtuos.getValueFromPlan(planStr, virtuos.KEY_PRESCRIBED_DOSE)
      
      planArtefact[artefactProps.PLANNED_FRACTIONS] = int(fractionNR)
      planArtefact[artefactProps.PRESCRIBED_DOSE] = float(prescribedDose)
    except:
      logger.warning("Unable to add plan properties to artefact. Artefact: %s", str(planArtefact))
      raise
      
    
    
  def _postProcessCLIExecution(self):
    
    self._copyResults()

    plan = artefactHelper.getArtefactProperty(self._plan,artefactProps.URL)
    newPlan = artefactHelper.getArtefactProperty(self._resultPlanArtefact,artefactProps.URL)
    
    virtuos.normalizePlanFile(newPlan, plan)
    
    self._addPlanProperties(self._resultPlanArtefact)   



class pdcBatchAction(BatchActionBase):    
  '''Action for batch processing of the pdc++.'''
  
  def __init__(self,  imageSelector, planSelector, structSelector,
               planLinker = FractionLinker(useClosestPast = True), structLinker = FractionLinker(),
               actionTag = "pdc", alwaysDo = False,
               session = None, additionalActionProps = None,
               scheduler = SimpleScheduler(),**singleActionParameters):
    
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._images = imageSelector.getSelection(self._session.artefacts)
    self._plans = planSelector.getSelection(self._session.artefacts)
    self._structs = structSelector.getSelection(self._session.artefacts)
   
    self._planLinker = planLinker
    self._structLinker = structLinker  
    self._singleActionParameters = singleActionParameters

      
  def _generateActions(self):
    #filter only type result. Other artefact types are not interesting
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)
    
    images = self.ensureRelevantArtefacts(self._images, resultSelector, "pdc images")
    plans = self.ensureRelevantArtefacts(self._plans, resultSelector, "pdc plans")
    structs = self.ensureRelevantArtefacts(self._structs, resultSelector, "pdc structs")
     
    actions = list()
    
    for (pos,image) in enumerate(images):
      linkedPlans = self._planLinker.getLinkedSelection(pos,images,plans)       

      for (planPos, lplan) in enumerate(linkedPlans):
        linkedstructs = self._structLinker.getLinkedSelection(planPos, linkedPlans, structs)
        for lstruct in linkedstructs:

          action = pdcAction(image, lplan, lstruct, self._actionTag,
                             alwaysDo = self._alwaysDo, session = self._session,
                             additionalActionProps = self._additionalActionProps,
                             **self._singleActionParameters)
          actions.append(action)
    
    return actions