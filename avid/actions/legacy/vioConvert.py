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
from . import BatchActionBase
from .cliActionBase import CLIActionBase
from avid.selectors import TypeSelector
from .simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)


class VioConvertAction(CLIActionBase):
  '''Class that wrapps the single action for the tool vioConvert.'''

  def __init__(self, inputFile, desiredOutputFormat="nrrd", rescale=False, actionTag="vioConvert", alwaysDo=False,
               session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=dict()):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig=actionConfig, propInheritanceDict=propInheritanceDict)
    self._addInputArtefacts(input=inputFile)
    self._inputFile = inputFile
    self._desiredOutputFormat = desiredOutputFormat
    self._rescale = rescale

    cwd = os.path.dirname(AVIDUrlLocater.getExecutableURL(self._session, "VioConvert", actionConfig))
    self._cwd = cwd

  def _generateName(self):
    name = "vioConvert_"+str(artefactHelper.getArtefactProperty(self._inputFile, artefactProps.ACTIONTAG))\
            + "_#" + str(artefactHelper.getArtefactProperty(self._inputFile, artefactProps.TIMEPOINT))
    return name
    
  def _indicateOutputs(self):
    
    artefactRef = self._inputFile
    
    name = self._generateName()

    # Specify result artefact
    self._resultArtefact = self.generateArtefact(artefactRef)
    self._resultArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._resultArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_ITK
    
    path = artefactHelper.generateArtefactPath(self._session, self._resultArtefact)
    resName = name + "." + str(artefactHelper.getArtefactProperty(self._resultArtefact, artefactProps.ID)) + os.extsep + self._desiredOutputFormat
    resName = os.path.join(path, resName)
    
    self._resultArtefact[artefactProps.URL] = resName

    return [self._resultArtefact]
        
  def _prepareCLIExecution(self):
    
    resultPath = artefactHelper.getArtefactProperty(self._resultArtefact, artefactProps.URL)
    inputPath = artefactHelper.getArtefactProperty(self._inputFile, artefactProps.URL)

    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])
    
    execURL = AVIDUrlLocater.getExecutableURL(self._session, "VioConvert", self._actionConfig)
    
    content = '"' + execURL + '"'
    content += ' "' + inputPath + '"'
    content += ' "' + resultPath + '"'
    if self._rescale is True:
      content += ' --rescale '

    return content


class VioConvertBatchAction(BatchActionBase):
  '''Action for batch processing of the regVarTool.'''

  def __init__(self, inputSelector, desiredOutputFormat="nrrd", rescale=False,
               actionTag="vioConvert", alwaysDo=False,
               session=None, additionalActionProps=None, scheduler=SimpleScheduler(),
               **singleActionParameters):
    
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._input = inputSelector.getSelection(self._session.artefacts)
    self._rescale = rescale
    self._desiredOutputFormat = desiredOutputFormat

    self._singleActionParameters = singleActionParameters

      
  def _generateActions(self):
    #filter only type result. Other artefact types are not interesting
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)
    
    relevantInput = self.ensureRelevantArtefacts(self._input, resultSelector, "input files")
      
    actions = list()
    
    for relevantFile in relevantInput:
      action = VioConvertAction(relevantFile, self._desiredOutputFormat, self._rescale, actionTag=self._actionTag, alwaysDo=self._alwaysDo, session=self._session,
                                additionalActionProps=self._additionalActionProps, **self._singleActionParameters)
      actions.append(action)
    
    return actions
