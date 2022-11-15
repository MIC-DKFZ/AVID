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
from .cliActionBase import CLIActionBase
from avid.linkers import FractionLinker
from avid.selectors import TypeSelector
from .simpleScheduler import SimpleScheduler
from avid.selectors.keyValueSelector import FormatSelector

logger = logging.getLogger(__name__)

class combineRAction(CLIActionBase):
  '''Class that wrapps the single action for the tool combineR.'''

  def __init__(self, reg1, reg2, combOperation = "+", 
               actionTag = "combineR", alwaysDo = False,
               session = None, additionalActionProps = None, actionConfig = None, propInheritanceDict = None):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig = actionConfig,
                           propInheritanceDict=propInheritanceDict)
    self._addInputArtefacts(reg1=reg1,reg2=reg2)

    self._reg1 = reg1
    self._reg2 = reg2
    self._combOp = combOperation

  def _generateName(self):
    name = "combineR_"+str(artefactHelper.getArtefactProperty(self._reg1,artefactProps.ACTIONTAG))\
            +"_#"+str(artefactHelper.getArtefactProperty(self._reg1,artefactProps.TIMEPOINT))+"_"+self._combOp\
            +"_"+str(artefactHelper.getArtefactProperty(self._reg2,artefactProps.ACTIONTAG))\
              +"_#"+str(artefactHelper.getArtefactProperty(self._reg2,artefactProps.TIMEPOINT))
    return name
   
  def _indicateOutputs(self):
    
    self._resultArtefact = self.generateArtefact(self._reg1,
                                                 userDefinedProps={artefactProps.TYPE:artefactProps.TYPE_VALUE_RESULT, artefactProps.FORMAT:artefactProps.FORMAT_VALUE_MATCHPOINT},
                                                 urlHumanPrefix=self.instanceName,
                                                 urlExtension='mapr')

    return [self._resultArtefact]

      
  def _prepareCLIExecution(self):
    
    resultPath = artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.URL)
    reg1Path = artefactHelper.getArtefactProperty(self._reg1,artefactProps.URL)
    reg2Path = artefactHelper.getArtefactProperty(self._reg2,artefactProps.URL)
    
    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])
    
    execURL = self._cli_connector.get_executable_url(self._session, "combineR", self._actionConfig)
    
    content = '"'+ execURL + '"' + ' "' + resultPath + '" "' + reg1Path +'" '+self._combOp+'"' + reg2Path + '"'

    return content


class combineRBatchAction(BatchActionBase):    
  '''Batch action for combineR.'''

  def __init__(self,  reg1Selector, reg2Selector,
               regLinker = FractionLinker(),
               actionTag = "combineR", alwaysDo = False, session = None,
               additionalActionProps = None, scheduler = SimpleScheduler(), **singleActionParameters):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._reg1s = reg1Selector.getSelection(self._session.artefacts)
    self._reg2s = reg2Selector.getSelection(self._session.artefacts)

    self._regLinker = regLinker
    self._singleActionParameters = singleActionParameters

      
  def _generateActions(self):
    #filter only type result. Other artefact types are not interesting
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)+FormatSelector(artefactProps.FORMAT_VALUE_MATCHPOINT)
    
    reg1s = self.ensureRelevantArtefacts(self._reg1s, resultSelector, "combineR registrations 1")
    reg2s = self.ensureRelevantArtefacts(self._reg2s, resultSelector, "combineR registrations 2")

    global logger

    actions = list()
    
    for (pos,reg1) in enumerate(reg1s):
      linkedRegs = self._regLinker.getLinkedSelection(pos,reg1s, reg2s)
      if len(linkedRegs) == 0:
        logger.debug("Linked reg2 selection contains no usable artefacts. For reg1 no combinations will be generated. Reg1: %s", str(reg1))    

      for reg2 in linkedRegs:
        action = combineRAction(reg1, reg2,
                                actionTag=self._actionTag,
                                alwaysDo = self._alwaysDo,
                                session = self._session,
                                additionalActionProps = self._additionalActionProps,
                                **self._singleActionParameters)
        actions.append(action)
    
    return actions
