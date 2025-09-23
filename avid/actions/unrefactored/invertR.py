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

import logging
import os
from builtins import str

import avid.common.artefact as artefactHelper
import avid.common.artefact.defaultProps as artefactProps
from avid.actions import BatchActionBase
from avid.actions.cliActionBase import CLIActionBase
from avid.actions.simpleScheduler import SimpleScheduler
from avid.common import AVIDUrlLocater, osChecker
from avid.externals.matchPoint import FORMAT_VALUE_MATCHPOINT
from avid.linkers import FractionLinker
from avid.selectors import TypeSelector

logger = logging.getLogger(__name__)


class invertRAction(CLIActionBase):
  '''Class that wrapps the single action for the tool invertR.'''

  def __init__(self, registration, templateImage=None, directMapping=False, inverseMapping=False, actionTag="invertR", alwaysDo=False,
               session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig=actionConfig,
                           propInheritanceDict=propInheritanceDict)
    self._addInputArtefacts(registration=registration, templateImage=templateImage)

    self._registration = registration
    self._templateImage = templateImage
    self._directMapping = directMapping
    self._inverseMapping = inverseMapping

    cwd = os.path.dirname(AVIDUrlLocater.get_tool_executable_url(self._session, "invertR", actionConfig))
    self._cwd = cwd

  def _generateName(self):
    name = "regInv_" + str(artefactHelper.getArtefactProperty(self._registration, artefactProps.ACTIONTAG))\
            + "_#" + str(artefactHelper.getArtefactProperty(self._registration, artefactProps.TIMEPOINT))
    if self._templateImage is not None:
      name += "_to_" + str(artefactHelper.getArtefactProperty(self._templateImage, artefactProps.ACTIONTAG))\
            + "_#"+str(artefactHelper.getArtefactProperty(self._templateImage, artefactProps.TIMEPOINT))

    return name

  def _indicateOutputs(self):
    artefactRef = self._registration

    # Specify result artefact
    self._resultArtefact = self.generateArtefact(artefactRef,
                                                 userDefinedProps = {artefactProps.TYPE: artefactProps.TYPE_VALUE_RESULT,
                                                                   artefactProps.FORMAT: FORMAT_VALUE_MATCHPOINT},
                                                 url_user_defined_part=self._generateName(),
                                                 url_extension='mapr')

    return [self._resultArtefact]

  def _prepareCLIExecution(self):
    resultPath = artefactHelper.getArtefactProperty(self._resultArtefact, artefactProps.URL)

    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])

    try:
      execURL = self._cli_connector.get_executable_url(self._session, "invertR", self._actionConfig)
      registrationURL = artefactHelper.getArtefactProperty(self._registration, artefactProps.URL)
      if self._templateImage is not None:
        templateImageURL = artefactHelper.getArtefactProperty(self._templateImage, artefactProps.URL)

      content = '"' + execURL + '"'
      content += ' "' + registrationURL + '"'
      content += ' --output "' + resultPath + '"'
      if self._templateImage is not None:
        content += ' --FOVtemplate ' + ' "' + templateImageURL + '"'
      if self._directMapping is True:
        content += ' --directMapping'
      if self._inverseMapping is True:
        content += ' --inverseMapping'

    except:
      logger.error("Error for getExecutable.")
      raise

    return content


class invertRBatchAction(BatchActionBase):
  '''Action for batch processing of the invertR.'''

  def __init__(self, registrationSelector, templateSelector= None, templateLinker = FractionLinker(), directMapping=False, inverseMapping=False, actionTag="invertR", alwaysDo=False,
               session=None, additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._registrations = registrationSelector.getSelection(self._session.artefacts)
    self._templateImages = list()
    if templateSelector is not None:
      self._templateImages = templateSelector.getSelection(self._session.artefacts)

    self._templateLinker = templateLinker
    self._directMapping = directMapping
    self._inverseMapping = inverseMapping

    self._singleActionParameters = singleActionParameters

  def _generateActions(self):
    # filter only type result. Other artefact types are not interesting
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)

    registrations = self.ensureRelevantArtefacts(self._registrations, resultSelector, "invertR registrations")
    templateImages = self.ensureRelevantArtefacts(self._templateImages, resultSelector, "invertR template images")

    global logger

    actions = list()

    for (pos, registration) in enumerate(registrations):
      if len(templateImages) == 0:
        linkedTemplateImages = [None]
      else :
        linkedTemplateImages = self._templateLinker.getLinkedSelection(pos, registrations, templateImages)

      for ti in linkedTemplateImages:
        action = invertRAction(registration, templateImage=ti, directMapping=self._directMapping, inverseMapping=self._inverseMapping, actionTag=self._actionTag,
                           alwaysDo=self._alwaysDo, session=self._session, additionalActionProps=self._additionalActionProps, **self._singleActionParameters)
        actions.append(action)
    return actions
