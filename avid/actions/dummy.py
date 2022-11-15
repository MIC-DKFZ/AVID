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

from ..actions import BatchActionBase
from avid.actions import SingleActionBase
from avid.actions.cliActionBase import CLIActionBase
import avid.common.artefact as artefactHelper
import avid.common.artefact.defaultProps as artefactProps
from .simpleScheduler import SimpleScheduler
from avid.common import osChecker, AVIDUrlLocater

class DummySingleAction(SingleActionBase):

  def __init__(self, artefacts, actionTag, alwaysDo = False, session = None, additionalActionProps = None, propInheritanceDict = None):
    SingleActionBase.__init__(self, actionTag,alwaysDo,session, additionalActionProps = additionalActionProps, propInheritanceDict = propInheritanceDict )
    self._artefacts = artefacts

    inputs = dict()
    for pos, a in enumerate(artefacts):
      inputs['i'+str(pos)] = [a]

    self._addInputArtefacts(**inputs)
    self.callCount_generateOutputs = 0

  def _generateName(self):
    name = "Dummy"
    return name

  def _indicateOutputs(self):
    return self._artefacts

  def _generateOutputs(self):
    self.callCount_generateOutputs = self.callCount_generateOutputs + 1
    pass


class DummyBatchAction(BatchActionBase):
  def __init__(self, artefactSelector, actionTag = 'Dummy', scheduler = SimpleScheduler(), session = None,
               additionalActionProps = None, **singleActionParameters):

    BatchActionBase.__init__(self, actionTag= actionTag, actionClass=DummySingleAction, primaryInputSelector= artefactSelector,
                             primaryAlias="artefacts", session= session, scheduler=scheduler,
                             additionalActionProps = additionalActionProps, **singleActionParameters)


class DummyCLIAction(CLIActionBase):
  '''Class that wraps the single action for the AVID dummy cli.'''

  def __init__(self, input,
               actionTag = "DummyCLI", alwaysDo = False,
               session = None, additionalActionProps = None, actionConfig = None):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, None, actionConfig = None)

    self._addInputArtefacts(input = input)

    self._input = input

  def _generateName(self):
    name = "Dummy_of_"+str(artefactHelper.getArtefactProperty(self._input,artefactProps.ACTIONTAG))

    return name

  def _indicateOutputs(self):

    self._resultArtefact = self.generateArtefact(self._input,
                                                 userDefinedProps={artefactProps.TYPE:artefactProps.TYPE_VALUE_RESULT,
                                                                   artefactProps.FORMAT: artefactProps.FORMAT_VALUE_CSV},
                                                 urlHumanPrefix=self.instanceName,
                                                 urlExtension='txt')
    return [self._result]


  def _prepareCLIExecution(self):

    resultPath = artefactHelper.getArtefactProperty(self._result,artefactProps.URL)
    inputPath = artefactHelper.getArtefactProperty(self._input,artefactProps.URL)

    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])

    execURL = self._cli_connector.get_executable_url(self._session, "CLIDummy", self._actionConfig)

    content = '"' + execURL + '" "'+str(resultPath)+'" "'+str(inputPath)+'" "Dummytest"'

    return content


class DummyCLIBatchAction(BatchActionBase):
  def __init__(self, artefacts, actionTag = 'DummyCLI', alwaysDo = False, scheduler = SimpleScheduler(), session = None):

    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session = session)
    self._artefacts = artefacts

    BatchActionBase.__init__(self, actionTag= actionTag, actionClass=DummyCLIAction, primaryInputSelector= targetSelector,
                             primaryAlias="targetImage", additionalInputSelectors = additionalInputSelectors,
                             linker = linker, dependentLinker=dependentLinker, session= session,
                             relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                             scheduler=scheduler, additionalActionProps = additionalActionProps, **singleActionParameters)



  def _generateActions(self):
    actions = []
    for artefact in self._artefacts:
      action = DummyCLIAction(artefact, alwaysDo = self._alwaysDo, session = self._session)
      actions.append(action)

    return actions
