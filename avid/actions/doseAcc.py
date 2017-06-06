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
from avid.sorter import TimePointSorter
from simpleScheduler import SimpleScheduler
from doseMap import _getArtefactLoadStyle 
from avid.externals.matchPoint import ensureMAPRegistrationArtefact
import avid.common.demultiplexer as demux

logger = logging.getLogger(__name__)


class DoseAccAction(CLIActionBase):
  '''Class that wraps the single action for the tool doseAcc.'''

  def __init__(self, dose1, dose2, registration=None, weight1=None, weight2=None, interpolator="linear", operator="+", outputExt="nrrd",
               actionTag="doseAcc", alwaysDo=False, session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig=actionConfig,
                           propInheritanceDict=propInheritanceDict)
    self._addInputArtefacts(dose1=dose1, dose2=dose2, registration=registration)

    self._dose1 = dose1
    self._registration = registration
    self._dose2 = dose2
    self._weight1 = weight1
    self._weight2 = weight2
    self._interpolator = interpolator
    self._operator = operator
    self._outputExt = outputExt
    self._resultArtefact = None

    cwd = os.path.dirname(AVIDUrlLocater.getExecutableURL(self._session, "DoseAcc", actionConfig))
    self._cwd = cwd

  def _generateName(self):
    # need to define the outputs
    name = "doseAcc_"+str(artefactHelper.getArtefactProperty(self._dose1, artefactProps.ACTIONTAG)) \
           + "_#"+str(artefactHelper.getArtefactProperty(self._dose1, artefactProps.TIMEPOINT))

    if self._operator == "+":
      name += "_a_"
    elif self._operator == "*":
      name += "_m_"
    else:
      logger.error("operator %s not known.", self._operator)
      raise

    name += str(artefactHelper.getArtefactProperty(self._dose2, artefactProps.ACTIONTAG)) \
            + "_#"+str(artefactHelper.getArtefactProperty(self._dose2, artefactProps.TIMEPOINT))

    if self._registration is not None:
      name += "_by_"+str(artefactHelper.getArtefactProperty(self._registration, artefactProps.ACTIONTAG)) \
              + "_#" + str(artefactHelper.getArtefactProperty(self._registration, artefactProps.TIMEPOINT))
    else:
      name += "_by_identity"

    return name

  def _indicateOutputs(self):

    if self._resultArtefact is None:
      self._resultArtefact = self.generateArtefact(self._dose2,
                                                   userDefinedProps={
                                                     artefactProps.TYPE: artefactProps.TYPE_VALUE_RESULT,
                                                     artefactProps.FORMAT: artefactProps.FORMAT_VALUE_ITK},
                                                   urlHumanPrefix=self.instanceName,
                                                   urlExtension=self._outputExt)

    return [self._resultArtefact]

  def _prepareCLIExecution(self):

    resultPath = artefactHelper.getArtefactProperty(self._resultArtefact, artefactProps.URL)
    dose1Path = artefactHelper.getArtefactProperty(self._dose1, artefactProps.URL)
    dose2Path = artefactHelper.getArtefactProperty(self._dose2, artefactProps.URL)
    registrationPath = artefactHelper.getArtefactProperty(self._registration, artefactProps.URL)

    result = ensureMAPRegistrationArtefact(self._registration, self.generateArtefact(self._dose2), self._session)
    if result[0]:
      if result[1] is None:
        logger.error("Dose accumulation will fail. Given registration is not MatchPoint compatible and cannot be converted.")
      else:
        registrationPath = artefactHelper.getArtefactProperty(result[1], artefactProps.URL)
        logger.debug("Converted/Wrapped given registration artefact to be MatchPoint compatible. Wrapped artefact path: " + registrationPath)

    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])

    execURL = AVIDUrlLocater.getExecutableURL(self._session, "DoseAcc", self._actionConfig)

    content = '"'+execURL + '"' + ' "' + dose1Path + '"' + ' "' + dose2Path + '"' + ' "' + resultPath + '"'

    if registrationPath is not None:
      content += ' --registration "' + registrationPath + '"'

    if self._weight1 is not None:
      content += ' --weight1 "' + str(self._weight1) + '"'

    if self._weight2 is not None:
      content += ' --weight2 "' + str(self._weight2) + '"'

    content += ' --interpolator ' + self._interpolator

    content += ' --operator ' + self._operator

    content += ' --loadStyle1 ' + _getArtefactLoadStyle(self._dose1)
    content += ' --loadStyle2 ' + _getArtefactLoadStyle(self._dose2)

    return content


def _getFractionWeight(artefact):
  fractions = artefactHelper.getArtefactProperty(artefact, artefactProps.PLANNED_FRACTIONS)
  result = None
  try:
    result = 1 / float(fractions)
  except:
    pass

  return result


class DoseAccBatchAction(BatchActionBase):
  '''This action accumulates a whole selection of doses and stores the
  Remark. The doses will be sorted before accumulation (incremental) results.'''

  def __init__(self,  doseSelector, registrationSelector=None, planSelector=None,
               regLinker=FractionLinker(), planLinker=FractionLinker(useClosestPast=True), doseSorter=TimePointSorter(),
               doseSplitProperty = None, interpolator="linear", operator="+",
               actionTag="doseAcc", alwaysDo=False,
               session=None, additionalActionProps=None, **singleActionParameters):
    BatchActionBase.__init__(self, actionTag, alwaysDo, SimpleScheduler(), session, additionalActionProps)

    self._doses = doseSelector.getSelection(self._session.artefacts)

    self._registrations = list()
    if registrationSelector is not None:
      self._registrations = registrationSelector.getSelection(self._session.artefacts)

    self._plans = list()
    if planSelector is not None:
      self._plans = planSelector.getSelection(self._session.artefacts)

    self._regLinker = regLinker
    self._planLinker = planLinker
    self._doseSorter = doseSorter
    self._singleActionParameters = singleActionParameters
    self._doseSplitProperty = doseSplitProperty
    self._operator = operator
    self._interpolator = interpolator

  def _generateActions(self):
    # filter only type result. Other artefact types are not interesting
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)

    allDoses = self.ensureRelevantArtefacts(self._doses, resultSelector, "doseAcc doses")
    regs = self.ensureRelevantArtefacts(self._registrations, resultSelector, "doseAcc regs")
    plans = self.ensureRelevantArtefacts(self._plans, resultSelector, "doseAcc plans")

    splittedDoses = list()

    if self._doseSplitProperty is not None:
      splitDict = demux.getSelectors(str(self._doseSplitProperty), workflowData=allDoses)
      for splitID in splitDict:
        relevantDoseSelector = splitDict[splitID]
        relevantInputs = relevantDoseSelector.getSelection(allDoses)
        splittedDoses.append(relevantInputs)
    else:
      splittedDoses.append(allDoses)

    actions = list()

    for doses in splittedDoses:
      doses = self._doseSorter.sortSelection(doses)
      for (pos, dose) in enumerate(doses):
        weight2 = 1.0/len(doses)
        linkedPlans = self._planLinker.getLinkedSelection(pos, doses, plans)

        if len(linkedPlans) > 0:
          # deduce weight by planned fraction number
          lPlan = linkedPlans[0]
          planWeight = _getFractionWeight(lPlan)
          if planWeight is None:
            logger.warning("Selected plan has no fraction number information. Cannot determine fraction weight. \
            Fall back to default strategy (weight: %s). Used plan artefact: %s", weight2, lPlan)
          else:
            weight2 = planWeight

          if len(linkedPlans) > 1:
            logger.warning("Improper selection of plans. Multiple plans for one dose/fraction selected. Action assumes only one plan linked per dose. \
            Use first plan. Drop other plan. Used plan artefact: %s", lPlan)
        else:
          logger.info("No plan selected, no fraction number information available. Cannot determine fraction weight. \
          Fall back to default strategy (1/number of selected doses => weight: %s).", weight2)

        linkedRegs = self._regLinker.getLinkedSelection(pos, doses, regs)
        lReg = None
        if len(linkedRegs) > 0:
          lReg = linkedRegs[0]
          if len(linkedRegs) > 1:
            logger.warning("Improper selection of registrations. Multiple registrations for one dose/fraction selected. \
            Action assumes only one registration linked per dose. Use first registration. Drop other registrations. Used registration: %s", lReg)

        additionalActionProps = {artefactProps.ACC_ELEMENT: str(pos)}

        if self._additionalActionProps is not None:
          additionalActionProps.update(self._additionalActionProps)

        if pos == 0:
          # first element should be handled differently
          if self._operator is not "*":
            action = DoseAccAction(dose, dose, lReg, 0.0, weight2, interpolator=self._interpolator,
                                   operator=self._operator,
                                   actionTag=self._actionTag, alwaysDo=self._alwaysDo,
                                   session=self._session,
                                   additionalActionProps=additionalActionProps,
                                   **self._singleActionParameters)
          else:
            action = None
        else:
          if not actions and self._operator is "*":
            interimDoseArtefact = doses[0]
          else:
            interimDoseArtefact = actions[-1]._resultArtefact # take the dose result of the last action
          if self._operator is "*":
            weight2 = 1.0
          action = DoseAccAction(interimDoseArtefact, dose, lReg, 1.0, weight2, interpolator=self._interpolator,
                                 operator=self._operator,
                                 actionTag=self._actionTag, alwaysDo=self._alwaysDo,
                                 session=self._session,
                                 additionalActionProps=additionalActionProps,
                                 **self._singleActionParameters)

        if action is not None:
          action._indicateOutputs() # call to ensure the result artefact is defined
          actions.append(action)

    return actions
