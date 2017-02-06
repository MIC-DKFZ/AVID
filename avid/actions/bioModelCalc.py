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
from . import BatchActionBase
from cliActionBase import CLIActionBase
from avid.linkers import FractionLinker
from avid.selectors import TypeSelector
from simpleScheduler import SimpleScheduler
from doseMap import _getArtefactLoadStyle
from doseAcc import _getFractionWeight
import avid.externals.virtuos as virtuos

logger = logging.getLogger(__name__)

class BioModelCalcAction(CLIActionBase):
  '''Class that wraps the single action for the tool doseMap.'''

  def __init__(self, inputDose, weight=1.0, nFractions=1, modelParameters=[0.1,0.01], modelParameterMaps = list(), modelName="LQ", outputExt="nrrd",
               actionTag = "DoseStat", alwaysDo = False, session = None,
               additionalActionProps = None, actionConfig = None, propInheritanceDict = dict()):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig = actionConfig,
                           propInheritanceDict = propInheritanceDict)
    self._addInputArtefacts(inputDose=inputDose)
    self._inputDose = inputDose
    self._weight = weight
    self._nFractions = nFractions
    self._modelParameters = modelParameters
    self._modelParameterMaps = modelParameterMaps
    self._modelName = modelName
    self._outputExt = outputExt
    
  def _generateName(self):
    name = "bioModelCalc_"

    name += "__"+str(artefactHelper.getArtefactProperty(self._inputDose,artefactProps.ACTIONTAG))\
            +"_#"+str(artefactHelper.getArtefactProperty(self._inputDose,artefactProps.TIMEPOINT))
    return name
   
  def _indicateOutputs(self):
    
    name = self.instanceName

    self._resultArtefact = self.generateArtefact(self._inputDose)
    self._resultArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._resultArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_ITK
    
    path = artefactHelper.generateArtefactPath(self._session, self._resultArtefact)
    resName = name + "." + str(artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.ID)) + os.extsep + self._outputExt
    resName = os.path.join(path, resName)
    
    self._resultArtefact[artefactProps.URL] = resName

    return [self._resultArtefact]
 
                
  def _prepareCLIExecution(self):
    
    resultPath = artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.URL)
    inputPath = artefactHelper.getArtefactProperty(self._inputDose,artefactProps.URL)

    
    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])
    
    execURL = AVIDUrlLocater.getExecutableURL(self._session, "BioModelCalc", self._actionConfig)
    
    content = '"' + execURL + '"' + ' --dose "' + inputPath+ '"'
    content += ' --loadStyle ' + _getArtefactLoadStyle(self._inputDose)
    content += ' --outputFile "' + resultPath + '"'
    content += ' --doseScaling ' + str(self._weight)
    content += ' --model "'+ self._modelName +'"'
    if self._modelParameterMaps:
      content += ' --modelParameterMaps '
      for val in self._modelParameterMaps:
        mapsPath = artefactHelper.getArtefactProperty(val, artefactProps.URL)
        content += mapsPath + " "
      content += ' --loadStyleParameterMaps ' + _getArtefactLoadStyle(self._modelParameterMaps[0]) + " "
    else:
      content += ' --modelParameters '
      for val in self._modelParameters:
        content+= str(val) + " "
    content += ' --nFractions ' + str(self._nFractions)

    return content

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
        msg = "Cannot calculate dose statistic. Virtuos cube file not found. Struct file: "+aPath
        logger.error(msg)
        raise RuntimeError(msg)
          
    result = result + ' "' + ctxPath + '"'
  else:
    logger.info("No load style known for artefact format: %s", aFormat)
    
  return result


class BioModelCalcBatchAction(BatchActionBase):
  '''Base class for action objects that are used together with selectors and
    should therefore able to process a batch of SingleActionBased actions.'''
  
  def __init__(self,  inputSelector, planSelector=None, normalizeFractions= True, useDoseScaling=True,
               planLinker = FractionLinker(useClosestPast=True), modelParameters=[0.1,0.01],
               modelParameterMapsSelector = None,
               actionTag = "bioModelCalc", alwaysDo = False,
               session = None, additionalActionProps = None, scheduler = SimpleScheduler(), **singleActionParameters):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._inputDoses = inputSelector.getSelection(self._session.inData)
    if planSelector is not None:
        self._plan = planSelector.getSelection(self._session.inData)
    else:
        self._plan=None
    self._planLinker = planLinker
    self._normalizeFractions = normalizeFractions
    self._useDoseScaling = useDoseScaling

    if modelParameterMapsSelector is not None:
      self._modelParameterMaps = modelParameterMapsSelector.getSelection(self._session.inData)
      self._modelParameters = list()
    else:
      self._modelParameterMaps = None
      self._modelParameters = modelParameters

    self._singleActionParameters = singleActionParameters

      
  def _generateActions(self):
    #filter only type result. Other artefact types are not interesting
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)
    
    inputs = self.ensureRelevantArtefacts(self._inputDoses, resultSelector, "bioModelCalc doses")
    if self._plan is not None:
        aPlan = self.ensureRelevantArtefacts(self._plan, resultSelector, "plan")

    if self._modelParameterMaps is not None:
      validParameterMaps = self.ensureRelevantArtefacts(self._modelParameterMaps, resultSelector, "parameter maps")
    else :
      validParameterMaps = list()
       
    actions = list()
    
    for (pos,inputDose) in enumerate(inputs):
      weight = 1.0
      nFractions = 1
      if self._plan is not None:
          linkedPlans = self._planLinker.getLinkedSelection(pos,inputs,aPlan)

          if len(linkedPlans) > 0:
            #deduce weight by planned fraction number
            lPlan = linkedPlans[0]
            planWeight = _getFractionWeight(lPlan)
            if planWeight is None:
              logger.warning("Selected plan has no fraction number information. Cannot determine fraction weight. Fall back to default strategy (weight: %s). Used plan artefact: %s", weight, lPlan)
            else:
              weight = planWeight

            if len(linkedPlans) > 1:
              logger.warning("Improper selection of plans. Multiple plans for one dose/fraction selected. Action assumes only one plan linked per dose. Use first plan. Drop other plan. Used plan artefact: %s", lPlan)
          else:
            logger.info("No plan selected, no fraction number information available. Cannot determine fraction weight. Fall back to default strategy (1/number of selected doses => weight: %s).", weight)


      if self._normalizeFractions is True:
        nFractions = int(1/weight)
      if self._useDoseScaling is False:
        weight = 1.0

      action = BioModelCalcAction(inputDose, weight, nFractions, self._modelParameters, validParameterMaps,
                          actionTag = self._actionTag, alwaysDo = self._alwaysDo,
                          session = self._session,
                          additionalActionProps = self._additionalActionProps,
                          **self._singleActionParameters)
      actions.append(action)
    
    return actions