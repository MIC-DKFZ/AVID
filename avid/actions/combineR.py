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
import logging

import avid.common.artefact.defaultProps as artefactProps

from avid.externals.matchPoint import FORMAT_VALUE_MATCHPOINT

from . import BatchActionBase
from .genericCLIAction import GenericCLIAction
from avid.linkers import FractionLinker
from avid.selectors import TypeSelector
from .simpleScheduler import SimpleScheduler
from avid.selectors.keyValueSelector import FormatSelector

logger = logging.getLogger(__name__)

class combineRAction(GenericCLIAction):
  '''Class that wrapps the single action for the tool combineR.'''

  def __init__(self, reg1, reg2, combOperation = "+", 
               actionTag = "combineR", alwaysDo = False,
               session = None, additionalActionProps = None, actionConfig = None, propInheritanceDict = None, cli_connector=None):
      self._reg1 = [self._ensureSingleArtefact(reg1, "reg1")]
      self._reg2 = [self._ensureSingleArtefact(reg2, "reg2")]
      self._combOp = combOperation

      additionalArgs = dict()
      if combOperation:
          additionalArgs['combOperation'] = str(combOperation)

      argPositions = ['o', 'reg1', 'combOperation', 'reg2']

      GenericCLIAction.__init__(self, reg1=reg1, reg2=reg2, actionID="combineR", outputFlags=['o'],
                                additionalArgs=additionalArgs, argPositions= argPositions, illegalArgs= ['output', 'input'],
                                actionTag= actionTag, alwaysDo=alwaysDo, session=session,
                                additionalActionProps=additionalActionProps, actionConfig=actionConfig,
                                propInheritanceDict=propInheritanceDict, cli_connector=cli_connector,
                                defaultoutputextension='mapr')

class combineRBatchAction(BatchActionBase):    
  '''Batch action for combineR.'''

  def __init__(self, reg1sSelector, reg2sSelector, reg2Linker=None,
               reg1Splitter = None, reg2Splitter = None, reg1Sorter = None, reg2Sorter = None,
               actionTag="combineR", session=None,
               additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):

      if reg2Linker is None:
          reg2Linker = FractionLinker()

      additionalInputSelectors = {"reg2": reg2sSelector}
      linker = {"reg2": reg2Linker}

      sorter = None
      if reg1Sorter is not None or reg2Sorter is not None:
          sorter = {}
          if reg1Sorter is not None:
              sorter[BatchActionBase.PRIMARY_INPUT_KEY] = reg1Sorter
          if reg2Sorter is not None:
              sorter['reg2'] = reg2Sorter

      splitter = None
      if reg1Splitter is not None or reg2Splitter is not None:
          splitter = {}
          if reg1Splitter is not None:
              splitter[BatchActionBase.PRIMARY_INPUT_KEY] = reg1Splitter
          if reg2Splitter is not None:
              splitter['reg2'] = reg2Splitter

      BatchActionBase.__init__(self, actionTag=actionTag, actionClass=combineRAction,
                               primaryInputSelector=reg1sSelector,
                               primaryAlias="reg1", additionalInputSelectors = additionalInputSelectors,
                               linker = linker, splitter=splitter, sorter=sorter, session=session,
                               relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT)+FormatSelector(FORMAT_VALUE_MATCHPOINT),
                               scheduler=scheduler, additionalActionProps=additionalActionProps,
                               **singleActionParameters)
