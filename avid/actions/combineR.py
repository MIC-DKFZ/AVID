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
import logging

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper

from avid.common import osChecker, AVIDUrlLocater
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
                               linker = linker, splitter=splitter, sorter=sorter,
                               session=session, relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                               scheduler=scheduler, additionalActionProps=additionalActionProps,
                               **singleActionParameters)
