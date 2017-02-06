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

from ..actions import BatchActionBase
from avid.actions import SingleActionBase
from avid.actions.cliActionBase import CLIActionBase
import avid.common.artefact as artefactHelper
import avid.common.artefact.defaultProps as artefactProps
from simpleScheduler import SimpleScheduler
from avid.common import osChecker, AVIDUrlLocater

class DummySingleAction(SingleActionBase):

  def __init__(self, artefacts, actionTag, alwaysDo = False, session = None, additionalActionProps = None, propInheritanceDict = dict()):
    SingleActionBase.__init__(self, actionTag,alwaysDo,session, additionalActionProps = additionalActionProps, propInheritanceDict = propInheritanceDict )
    self._artefacts = artefacts

    inputs = dict()
    for pos, a in enumerate(artefacts):
      inputs['i'+str(pos)] = a

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
  def __init__(self, artefacts, actionTag = 'Dummy', alwaysDo = False, scheduler = SimpleScheduler(), session = None):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session = session)
    self._artefacts = artefacts

  def _generateActions(self):
    actions = []
    for artefact in self._artefacts:
      action = DummySingleAction([artefact],"InternAction",self._alwaysDo, self._session)
      actions.append(action)

    return actions


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

    name = self.instanceName

    self._result = self.generateArtefact(self._input)
    self._result[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._result[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_CSV

    path = artefactHelper.generateArtefactPath(self._session, self._result)
    resName = name + os.extsep+"txt"
    resName = os.path.join(path, resName)

    self._result[artefactProps.URL] = resName

    return [self._result]


  def _prepareCLIExecution(self):

    resultPath = artefactHelper.getArtefactProperty(self._result,artefactProps.URL)
    inputPath = artefactHelper.getArtefactProperty(self._input,artefactProps.URL)

    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])

    execURL = AVIDUrlLocater.getExecutableURL(self._session, "CLIDummy", self._actionConfig)

    content = '"' + execURL + '" "'+str(resultPath)+'" "'+str(inputPath)+'" "Dummytest"'

    return content


class DummyCLIBatchAction(BatchActionBase):
  def __init__(self, artefacts, actionTag = 'DummyCLI', alwaysDo = False, scheduler = SimpleScheduler(), session = None):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session = session)
    self._artefacts = artefacts

  def _generateActions(self):
    actions = []
    for artefact in self._artefacts:
      action = DummyCLIAction(artefact, alwaysDo = self._alwaysDo, session = self._session)
      actions.append(action)

    return actions
