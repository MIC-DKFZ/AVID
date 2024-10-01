# SPDX-FileCopyrightText: 2024, German Cancer Research Center (DKFZ), Division of Medical Image Computing (MIC)
#
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# or find it in LICENSE.txt.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from builtins import str
import os
import logging

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper
from avid.common import osChecker
from avid.actions import BatchActionBase
from avid.actions.cliActionBase import CLIActionBase
from avid.linkers import FractionLinker, CaseLinker
from avid.sorter import BaseSorter
from avid.actions.simpleScheduler import SimpleScheduler
from avid.actions.rttb.doseMap import _getArtefactLoadStyle
from avid.actions.rttb.doseAcc import _getFractionWeightByArtefact
import avid.externals.virtuos as virtuos

logger = logging.getLogger(__name__)

class BioModelCalcAction(CLIActionBase):
  '''Class that wraps the single action for the RTTB tool BioModelCalc.
    The current implementation expects only one input dose element per call.'''

  def __init__(self, inputDose, weight=None, nFractions=None, modelParameters=None, modelParameterMaps = None,
               plan = None, modelName="LQ", normalizeFractions= True, useDoseScaling=True, outputExt="nrrd",
               actionTag = "DoseStat", alwaysDo = False, session = None, additionalActionProps = None,
               actionConfig = None, propInheritanceDict = None, cli_connector = None):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig = actionConfig,
                           propInheritanceDict = propInheritanceDict, cli_connector = cli_connector)
    self._addInputArtefacts(inputDose=inputDose, plan = plan, modelParameterMaps = modelParameterMaps)
    self._inputDose = self._ensureSingleArtefact(inputDose, "inputDose")
    self._plan = self._ensureSingleArtefact(plan, "plan")

    self._modelParameterMaps = modelParameterMaps
    self._modelParameters = modelParameters
    if modelParameters is None and ( self._modelParameterMaps is None or len(self._modelParameterMaps) == 0):
      self._modelParameters = [0.1,0.01]

    self._modelName = modelName

    self._outputExt = outputExt

    self._weight = weight
    self._nFractions = nFractions
    self._normalizeFractions = normalizeFractions
    self._useDoseScaling = useDoseScaling


    if self._plan is not None:
      # deduce weight by planned fraction number
      planWeight = _getFractionWeightByArtefact(self._plan)
      if planWeight is None:
        logger.warning(
          "Selected plan has no fraction number information. Cannot determine fraction weight. Fall back to default strategy (user defined weight: %s). Used plan artefact: %s",
          self._weight, self._plan)
      else:
        self._weight = planWeight

    if self._plan is None:
      if self._weight is None:
        self._weight = 1.0
        logger.info(
          "No plan selected, no fraction weight specifed. Use default weight of 1.0.")
      if self._nFractions is None:
        self._nFractions = 1
        logger.info(
          "No plan selected, no number of fractions specifed. Use default number of 1.")

    if self._normalizeFractions is True:
      self._nFractions = int(1 // self._weight)
      logger.info(
        "Normalize fraction is true. Nr of fraction set to {}.".format(self._nFractions))

    if self._useDoseScaling is False:
      self._weight = 1.0
      logger.info(
        "Use dose scaling deactivated. Weight set to 1.0 for bio model computation.")

  def _generateName(self):
    name = "bioModelCalc_{}_{}".format(self._modelName, artefactHelper.getArtefactShortName(self._inputDose))
    return name
   
  def _indicateOutputs(self):

    resultArtefact = self.generateArtefact(self._inputDose,
                                                 userDefinedProps={artefactProps.TYPE:artefactProps.TYPE_VALUE_RESULT, artefactProps.FORMAT:artefactProps.FORMAT_VALUE_ITK},
                                                 urlHumanPrefix=self.instanceName,
                                                 urlExtension=self._outputExt)
    return [resultArtefact]
 
                
  def _prepareCLIExecution(self):
    
    resultPath = artefactHelper.getArtefactProperty(self.outputArtefacts[0],artefactProps.URL)
    inputPath = artefactHelper.getArtefactProperty(self._inputDose,artefactProps.URL)

    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])
    
    execURL = self._cli_connector.get_executable_url(self._session, "BioModelCalc", self._actionConfig)
    
    content = '"' + execURL + '"' + ' --dose "' + inputPath+ '"'
    content += ' --loadStyle ' + _getArtefactLoadStyle(self._inputDose)
    content += ' --outputFile "' + resultPath + '"'
    content += ' --doseScaling ' + str(self._weight)
    content += ' --model "'+ self._modelName +'"'
    if self._modelParameterMaps is not None and len(self._modelParameterMaps) > 0:
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
  
  def __init__(self,  inputSelector, planSelector=None, planLinker = None,
               modelParameterMapsSelector = None, modelParameterMapsLinker = None, modelParameterMapsSorter = None,
               actionTag = "bioModelCalc", session = None, additionalActionProps = None, scheduler = SimpleScheduler(),
               **singleActionParameters):

    if planLinker is None:
      planLinker = FractionLinker(useClosestPast=True)
    if modelParameterMapsLinker is None:
      modelParameterMapsLinker = CaseLinker()
    if modelParameterMapsSorter is None:
      modelParameterMapsSorter = BaseSorter()

    additionalInputSelectors = {"plan": planSelector, "modelParameterMaps": modelParameterMapsSelector}
    linker = {"plan": planLinker, "modelParameterMaps": modelParameterMapsLinker}
    sorter = {"modelParameterMaps": modelParameterMapsSorter}

    BatchActionBase.__init__(self, actionTag= actionTag, actionClass=BioModelCalcAction, primaryInputSelector= inputSelector,
                             primaryAlias="inputDose", additionalInputSelectors = additionalInputSelectors,
                             linker = linker, sorter=sorter, session= session,
                             scheduler=scheduler, additionalActionProps = additionalActionProps, **singleActionParameters)
