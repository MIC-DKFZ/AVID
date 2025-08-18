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

from avid.common import osChecker, AVIDUrlLocater
from avid.actions import BatchActionBase
from avid.actions.cliActionBase import CLIActionBase
from avid.linkers import CaseLinker, LinkerBase
from avid.linkers import FractionLinker
from avid.selectors import TypeSelector
from avid.actions.simpleScheduler import SimpleScheduler
import avid.externals.virtuos as virtuos
from avid.externals.matchPoint import ensureMAPRegistrationArtefact

logger = logging.getLogger(__name__)

class DoseMapAction(CLIActionBase):
  '''Class that wraps the single action for the tool doseMap.'''

  def __init__(self, inputDose, registration = None, templateDose = None,
               interpolator = "linear", outputExt = "nrrd", 
               actionTag = "doseMap", alwaysDo = False,
               session = None, additionalActionProps = None, actionConfig = None, propInheritanceDict = None,
               cli_connector = None):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionID="DoseMap",
                           actionConfig = actionConfig, propInheritanceDict=propInheritanceDict, cli_connector=cli_connector)
    self._addInputArtefacts(inputDoses=inputDose, registrations=registration, templateDose=templateDose)

    self._inputDose = self._ensureSingleArtefact(inputDose,"inputDose")
    self._registration = self._ensureSingleArtefact(registration,"registration")
    self._templateDose = self._ensureSingleArtefact(templateDose, "templateDose")
    self._interpolator = interpolator
    self._outputExt = outputExt

  def _generateName(self):
    name = "doseMap_"+artefactHelper.getArtefactShortName(self._inputDose)

    if self._registration is not None:
      name += "_reg_" + artefactHelper.getArtefactShortName(self._registration)
    else:
      name += "_identity"

    if self._templateDose is not None:
      name += "_to_"+artefactHelper.getArtefactShortName(self._templateDose)

    return name

  def _hasDICOMinput(self):
    return self._outputExt.lower() =="dcm" or self._outputExt.lower() == "ima"

  def _indicateOutputs(self):
    userDefinedProps = {artefactProps.TYPE: artefactProps.TYPE_VALUE_RESULT}
    if self._hasDICOMinput():
      userDefinedProps[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_DCM

    artefactRef = self._inputDose

    resultArtefact = self.generateArtefact(artefactRef, userDefinedProps = userDefinedProps,
                                           url_user_defined_part=self.instanceName, url_extension=self._outputExt)
    return [resultArtefact]

                
  def _prepareCLIExecution(self):
    
    resultPath = artefactHelper.getArtefactProperty(self.outputArtefacts[0],artefactProps.URL)
    inputPath = artefactHelper.getArtefactProperty(self._inputDose,artefactProps.URL)
    templatePath = artefactHelper.getArtefactProperty(self._templateDose,artefactProps.URL)
    registrationPath = artefactHelper.getArtefactProperty(self._registration,artefactProps.URL)

    result = ensureMAPRegistrationArtefact(self._registration, self.generateArtefact(self._inputDose), self._session)
    if result[0]:
      if result[1] is None:
        logger.error("Mapping will fail. Given registration is not MatchPoint compatible and cannot be converted.")
      else:
        registrationPath = artefactHelper.getArtefactProperty(result[1],artefactProps.URL)
        logger.debug("Converted/Wrapped given registration artefact to be MatchPoint compatible. Wrapped artefact path: "+registrationPath)
    
    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])
    
    execURL = self._cli_connector.get_executable_url(self._session, self._actionID, self._actionConfig)
    
    content = '"' + execURL + '"' + ' "' + inputPath + '"' + ' "' + resultPath + '"'
    if registrationPath is not None:
      content += ' --regFileName "' + registrationPath +'"'
    
    if templatePath is not None:
      content += ' --refDoseFile "' + templatePath + '"'
      content += ' --refDoseLoadStyle ' + _getArtefactLoadStyle(self._templateDose)
      
    content += ' --interpolator ' + self._interpolator
    
    content += ' --inputDoseLoadStyle ' + _getArtefactLoadStyle(self._inputDose)

    return content


def _getArtefactLoadStyle(artefact):
  'deduce the load style parameter for an artefact that should be input'
  aPath = artefactHelper.getArtefactProperty(artefact,artefactProps.URL)
  aFormat = artefactHelper.getArtefactProperty(artefact,artefactProps.FORMAT)
  
  result = ""
  
  if aFormat == artefactProps.FORMAT_VALUE_ITK:
    result = aFormat
  elif aFormat == artefactProps.FORMAT_VALUE_DCM:
    result = "dicom"
  elif aFormat == artefactProps.FORMAT_VALUE_HELAX_DCM:
    result = "helax"
  elif aFormat == artefactProps.FORMAT_VALUE_VIRTUOS:
    result = "virtuos"
    #for virtuos we also need the plan information, check if we have the according artefact property
    plan = artefactHelper.getArtefactProperty(artefact,artefactProps.VIRTUOS_PLAN_REF)

    if not plan:
      #we assume as fall back that the plan has the same path except the extension
      plan = virtuos.stripFileExtensions(aPath)+os.extsep+"pln"
        
    result = result + ' "' + plan + '"'
  else:
    logger.info("No load style known for artefact format: %s", aFormat)
    
  return result


class DoseMapBatchAction(BatchActionBase):    
  '''Standard batch action class for DoseMap actions.'''
  
  def __init__(self,  inputSelector, registrationSelector = None, templateSelector = None,
               regLinker = None, templateLinker = None, templateRegLinker = None,
               actionTag = "doseMap", session = None, additionalActionProps = None, scheduler = SimpleScheduler(),
               **singleActionParameters):
    '''@param inputSelector Selector for the dose artefacts that should be mapped.
    @param registrationSelector Selector for the artefacts that specify the registration. If no registrations are
    specified, an identity transform will be assumed.
    @param templateSelector Selector for the reference geometry that should be used to map into it. If None is
    specified, the geometry of the input will be used.
    @param regLinker Linker to select the registration that should be used on an input. Default is FractionLinker.
    @param templateLinker Linker to select the reference geometry that should be used to map an input. Default is CaseLinker.
    @param templateRegLinker Linker to select which regs (resulting from the regLinker should be used regarding
    the template that will be used. Default is LinkerBase (so every link registration will be used with every linked
    template.'''
    if regLinker is None:
      regLinker = FractionLinker()
    if templateLinker is None:
      templateLinker = CaseLinker()
    if templateRegLinker is None:
      templateRegLinker = LinkerBase()

    additionalInputSelectors = {"registration": registrationSelector, "templateDose": templateSelector}
    linker = {"registration": regLinker, "templateDose": templateLinker}
    dependentLinker = {"registration": ("templateDose",templateRegLinker)}

    BatchActionBase.__init__(self, actionTag= actionTag, actionClass=DoseMapAction, primaryInputSelector= inputSelector,
                             primaryAlias="inputDose", additionalInputSelectors = additionalInputSelectors,
                             linker = linker, dependentLinker=dependentLinker, session= session,
                             relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                             scheduler=scheduler, additionalActionProps = additionalActionProps, **singleActionParameters)
