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

from builtins import str, enumerate
import os
import logging

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper

from avid.common import osChecker, AVIDUrlLocater
from avid.splitter import BaseSplitter
from . import BatchActionBase
from .cliActionBase import CLIActionBase
from avid.linkers import FractionLinker, LinkerBase, CaseLinker
from avid.selectors import TypeSelector
from avid.sorter import TimePointSorter
from .simpleScheduler import SimpleScheduler
from .doseMap import _getArtefactLoadStyle 
from avid.externals.matchPoint import ensureMAPRegistrationArtefact

logger = logging.getLogger(__name__)


def _getFractionWeightByArtefact(artefact, planned_fraction_property_name = artefactProps.PLANNED_FRACTIONS):
  '''Helper that deduces the fraction weight of an artefact'''
  fractions = artefactHelper.getArtefactProperty(artefact, planned_fraction_property_name)
  result = None
  try:
    result = 1 / float(fractions)
  except:
    pass

  return result

class DoseAccAction(CLIActionBase):
  '''Class that wraps the single action for the tool doseAcc.
     The action implements the following strategy to deduce the weights for the dose accumulation:
     1. If weight are set explicitly in __init__ they will always be used.
     2. If plans are set in __init__, the action will try to deducing the number of planned fractions and compute the
      weights accordingly.
     3. Action will try to deducing the number of planned fractions (stored in an artefact property)
     from the dose artefact.
     4. Action will assume (a) in case of + operation that the weight equals 1/number of doses or
      (b) in case of * operation that the weight equals 1.
  '''

  def __init__(self, doses, registrations=None, plans=None, weight=None,
               planned_fraction_property= artefactProps.PLANNED_FRACTIONS, interpolator="linear", operator="+",
               outputExt="nrrd", actionTag="doseAcc", alwaysDo=False, session=None,
               additionalActionProps=None, actionConfig=None, propInheritanceDict=None, cli_connector=None):
    ''':param doses: List of dose artefacts that should be accumulated.
       :param registrations: List of registration artefacts that should be used to map the doses befor accumulation.
       It is expected that this list is either None, a list equal in size to doses or a list that has one item less
       then doses (because the first dose will never be mapped.
       :param plans: list of plans that will be used to deduced to number of fractions and there for the accumulation
       weigth for each dose.
       :param weight: Possibility to set the weight that should be used for accumulating the doses.
       :type weights: float, int
       :param planned_fraction_property: Name of the property in the dose artefact or the plan artefact that encodes
       the number of fractions.
       :param interpolator: String that defines the interpolator that should be used. Is defined by doseAcc.
       :param operator: String that defines the type of accumulation. Is defined by doseAcc.
    '''
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionID = "doseAcc",
                           actionConfig=actionConfig, propInheritanceDict=propInheritanceDict, cli_connector=cli_connector)
    self._addInputArtefacts(doses=doses, registrations=registrations, plans= plans)

    self._doses = self._ensureArtefacts(doses, "doses")

    if len(self._doses)<2:
      raise RuntimeError('Cannot performe dose accumulation. Need at least two dose artefacts.')

    self._registrations = self._ensureArtefacts(registrations, "registrations")
    if self._registrations is not None:
      if len(self._registrations) == len(self._doses):
        logger.info("Number of doses ({}) equal the number of registrations. Assume that the first registration is"
                    " linked to the first dose. This registration will therefore be skipped.".format(len(self._doses)))
        self._registrations = self._registrations[1:]
      elif len(self._registrations)+1 == len(self._doses):
        logger.info("Number of doses ({}) exceeds the number of registrations ({}) by 1. Assume that the first"
                    " dose has no registration. This registration will therefore be skipped.".format(len(self._doses),
                                                                                                     len(self._registrations)))
      else:
        error ="Number of doses ({}) does not fit to number of registrations ({}); registration count must either be" \
               " equal or smaller by 1 (assuming that first dose is never mapped). Cannot performe action because" \
               " linking of the registrations to the doses is unclear.".format(len(self._doses),len(self._registrations))
        logger.error(error)
        raise RuntimeError(error)
    else:
      self._registrations = (len(self._doses)-1)*[None]

    self._plans = self._ensureArtefacts(plans, "plans")
    self._weight = weight

    if self._plans is not None:
      if self._weight is not None:
        logger.info("Plans and user specific weights have been defined. Plan information will be ignored.")
      elif not len(self._plans) == len(self._doses):
        error ="Number of doses ({}) does not fit to number of plans ({}). Cannot performe action because" \
               " linking of the registrations to the doses is unclear.".format(len(self._doses),len(self._plans))
        logger.error(error)
        raise RuntimeError(error)

    self._planned_fraction_property = planned_fraction_property
    self._interpolator = interpolator
    self._operator = operator
    self._outputExt = outputExt
    self._resultArtefact = None

  def _generateName(self):
    # need to define the outputs
    name = "doseAcc"

    if self._operator == "+":
      name += "_add_"
    elif self._operator == "*":
      name += "_multiply_"
    else:
      logger.error("operator %s not known.", self._operator)
      raise

    name += artefactHelper.getArtefactShortName(self._doses[0])
    name += "to_"+artefactHelper.getArtefactShortName(self._doses[-1])

    if self._registrations is not None:
      name += "_by_registration"
    else:
      name += "_by_identity"

    return name

  def _indicateOutputs(self):
    if self._resultArtefact is None:
      self._resultArtefact = self.generateArtefact(self._doses[-1],
                                                   userDefinedProps={
                                                     artefactProps.TYPE: artefactProps.TYPE_VALUE_RESULT,
                                                     artefactProps.FORMAT: artefactProps.FORMAT_VALUE_ITK,
                                                     artefactProps.ACC_ELEMENT: str(len(self._doses)-2)},
                                                   urlHumanPrefix=self.instanceName,
                                                   urlExtension=self._outputExt)

      self._interimArtefacts = list()
      for index, dose in enumerate(self._doses[1:-1]):
        self._interimArtefacts.append(self.generateArtefact(dose,
                                       userDefinedProps={
                                         artefactProps.TYPE: artefactProps.TYPE_VALUE_INTERIM,
                                         artefactProps.FORMAT: artefactProps.FORMAT_VALUE_ITK,
                                         artefactProps.ACC_ELEMENT: str(index)},
                                       urlHumanPrefix=self.instanceName+"_interim_{}".format(index),
                                       urlExtension=self._outputExt))

    return [self._resultArtefact]

  def _getFractionWeights(self):
    result = None

    if self._weight is not None:
      result = len(self._doses)*[self._weight]

    if result is None and self._plans is not None:
      result = list()
      for plan in self._plans:
        weight = _getFractionWeightByArtefact(plan, planned_fraction_property_name=self._planned_fraction_property)
        if weight is None:
          result = None
          break
        else:
          result.append(weight)

    if result is None:
      result = list()
      for dose in self._doses:
        weight = _getFractionWeightByArtefact(dose, planned_fraction_property_name=self._planned_fraction_property)
        if weight is None:
          result = None
          break
        else:
          result.append(weight)

    if result is None:
      if self._operator == '+':
        result = len(self._doses)*[1 / len(self._doses)]
      else:
        result = len(self._doses)*[1.0]

    return result

  def _generateCall(self, result, dose1, dose2, registration, weight1, weight2):
    resultPath = artefactHelper.getArtefactProperty(result, artefactProps.URL)
    dose1Path = artefactHelper.getArtefactProperty(dose1, artefactProps.URL)
    dose2Path = artefactHelper.getArtefactProperty(dose2, artefactProps.URL)
    registrationPath = artefactHelper.getArtefactProperty(registration, artefactProps.URL)

    result = ensureMAPRegistrationArtefact(registration, self.generateArtefact(dose2), self._session)
    if result[0]:
      if result[1] is None:
        logger.error("Dose accumulation will fail. Given registration is not MatchPoint compatible and cannot be converted.")
      else:
        registrationPath = artefactHelper.getArtefactProperty(result[1], artefactProps.URL)
        logger.debug("Converted/Wrapped given registration artefact to be MatchPoint compatible. Wrapped artefact path: " + registrationPath)

    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])

    execURL = self._cli_connector.get_executable_url(self._session, self._actionID, self._actionConfig)

    content = '"'+execURL + '"' + ' "' + dose1Path + '"' + ' "' + dose2Path + '"' + ' "' + resultPath + '"'

    if registrationPath is not None:
      content += ' --registration "' + registrationPath + '"'

    if weight1 is not None:
      content += ' --weight1 "' + str(weight1) + '"'

    if weight2 is not None:
      content += ' --weight2 "' + str(weight2) + '"'

    content += ' --interpolator ' + self._interpolator

    content += ' --operator ' + self._operator

    content += ' --loadStyle1 ' + _getArtefactLoadStyle(dose1)
    content += ' --loadStyle2 ' + _getArtefactLoadStyle(dose2)

    return content

  def _prepareCLIExecution(self):
    resultArtefacts = self._interimArtefacts + [self._resultArtefact]
    dose1Artefacts = [self._doses[0]] + self._interimArtefacts
    weight2s = self._getFractionWeights()
    weight1s = [weight2s[0]] + len(self._interimArtefacts)*[1]

    content = ""

    for index,resultArtefact in enumerate(resultArtefacts):
      if not len(content) == 0:
        content += os.linesep
      line = self._generateCall(result=resultArtefact, dose1=dose1Artefacts[index], dose2=self._doses[index+1],
                                registration=self._registrations[index], weight1=weight1s[index], weight2=weight2s[index+1])
      content += line

    return content


class DoseAccBatchAction(BatchActionBase):
  '''This action accumulates a whole selection of doses and stores the
  Remark. The doses will be sorted before accumulation (incremental) results.'''

  def __init__(self,  doseSelector, registrationSelector=None, planSelector=None,
               regLinker=None, planLinker=None, planRegLinker = None, doseSorter=None,
               doseSplitter = None, regSorter=None, regSplitter = None, planSorter=None,
               planSplitter = None, actionTag="doseAcc", session=None, additionalActionProps=None,
               scheduler = SimpleScheduler(), **singleActionParameters):

    if doseSorter is None:
      doseSorter = TimePointSorter()
    if doseSplitter is None:
      doseSplitter = BaseSplitter()

    if regSorter is None:
      regSorter = doseSorter
    if regSplitter is None:
      regSplitter = doseSplitter

    if planSorter is None:
      planSorter = doseSorter
    if planSplitter is None:
      planSplitter = doseSplitter

    if regLinker is None:
      regLinker = FractionLinker(performInternalLinkage=True, allowOnlyFullLinkage=False)
    if planLinker is None:
      planLinker = FractionLinker(useClosestPast=True, performInternalLinkage=True, allowOnlyFullLinkage=False)
    if planRegLinker is None:
      planRegLinker = CaseLinker(performInternalLinkage=False, allowOnlyFullLinkage=False)

    additionalInputSelectors = {"registrations": registrationSelector, "plans": planSelector}
    linker = {"registrations": regLinker, "plans": planLinker}
    dependentLinker = {"registrations": ("plans",planRegLinker)}
    sorter = {"doses": doseSorter, "registrations": regSorter, "plans": planSorter}
    splitter = {"doses": doseSplitter, "registrations": regSplitter, "plans": planSplitter}

    BatchActionBase.__init__(self, actionTag= actionTag, actionClass=DoseAccAction, primaryInputSelector= doseSelector,
                             primaryAlias="doses", additionalInputSelectors = additionalInputSelectors,
                             linker = linker, dependentLinker=dependentLinker, sorter=sorter, splitter=splitter,
                             session= session, relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                             scheduler=scheduler, additionalActionProps = additionalActionProps, **singleActionParameters)

