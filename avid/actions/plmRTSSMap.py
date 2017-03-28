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
from avid.externals.matchPoint import FORMAT_VALUE_MATCHPOINT, getDeformationFieldPath
from . import BatchActionBase
from cliActionBase import CLIActionBase
from avid.linkers import CaseLinker
from avid.selectors import TypeSelector
from simpleScheduler import SimpleScheduler
from avid.externals.plastimatch import parseDiceResult, FORMAT_VALUE_PLM_CXT
from avid.externals.doseTool import saveSimpleDictAsResultXML

logger = logging.getLogger(__name__)

class plmRTSSMap(CLIActionBase):
  '''Class that wraps the single action for the tool plastimatch convert in order to map DICOM RT SS via a registration.'''

  def __init__(self, rtss, reg, outputFormat = artefactProps.FORMAT_VALUE_DCM,
               actionTag = "plmRTSSMap", alwaysDo = False,
               session = None, additionalActionProps = None, actionConfig = None, propInheritanceDict = dict()):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig=actionConfig, propInheritanceDict=propInheritanceDict)
    self._addInputArtefacts(rtss=rtss, reg = reg)
    self._rtts = rtss
    self._reg = reg
    self._outputFormat = outputFormat

    self._cwd = os.path.dirname(AVIDUrlLocater.getExecutableURL(self._session, "plastimatch", actionConfig))
    
  def _generateName(self):
    name = "plmRTSSMap_"+str(artefactHelper.getArtefactProperty(self._rtss,artefactProps.ACTIONTAG))

    objective = artefactHelper.getArtefactProperty(self._rtss,artefactProps.OBJECTIVE)
    if not objective is None:
        name += '-%s'%objective

    name += "_#"+str(artefactHelper.getArtefactProperty(self._rtss,artefactProps.TIMEPOINT))\
            +"_by_"+str(artefactHelper.getArtefactProperty(self._reg,artefactProps.ACTIONTAG))

    objective = artefactHelper.getArtefactProperty(self._reg,artefactProps.OBJECTIVE)
    if not objective is None:
        name += '-%s'%objective

    name += "_#"+str(artefactHelper.getArtefactProperty(self._reg,artefactProps.TIMEPOINT))

    return name

  def _getOutputExtension(self):
    if self._outputFormat == artefactProps.FORMAT_VALUE_DCM:
      return 'dcm'
    elif self._outputFormat == FORMAT_VALUE_PLM_CXT:
      return 'cxt'
    else:
      raise ValueError('Output format is not supported by plmRTSSMap action. Choosen format: {}'.format(self._outputFormat))

  def _indicateOutputs(self):
    
    self._resultArtefact = self.generateArtefact(self._rtss,
                                                 userDefinedProps={artefactProps.TYPE:artefactProps.TYPE_VALUE_RESULT,
                                                                   artefactProps.FORMAT: self._outputFormat},
                                                 urlHumanPrefix=self.instanceName,
                                                 urlExtension=self._getOutputExtension())

    return [self._resultArtefact]

      
  def _prepareCLIExecution(self):
    
    rtssPath = artefactHelper.getArtefactProperty(self._rtss,artefactProps.URL)
    regPath = artefactHelper.getArtefactProperty(self._reg,artefactProps.URL)
    regFormat = artefactHelper.getArtefactProperty(self._reg,artefactProps.FORMAT)
    resultPath = artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.URL)

    if regFormat == FORMAT_VALUE_MATCHPOINT:
      regPath = getDeformationFieldPath(regPath)

    execURL = AVIDUrlLocater.getExecutableURL(self._session, "plastimatch", self._actionConfig)
    
    content = '"' + execURL + '" convert ' + ' --input "' + rtssPath + '"' + ' --xf "' + regPath

    if self._outputFormat == artefactProps.FORMAT_VALUE_DCM:
      content = content + ' --output-dicom "'+resultPath+'"'
    elif self._outputFormat == FORMAT_VALUE_PLM_CXT:
      content = content + ' --output-cxt "'+resultPath+'"'
    else:
      raise ValueError('Output format is not supported by plmRTSSMap action. Choosen format: {}'.format(self._outputFormat))
      
    return content


class plmRTSSMapBatchAction(BatchActionBase):
  '''Base class for action objects that are used together with selectors and
    should therefore able to process a batch of SingleActionBased actions.'''
  
  def __init__(self,  refSelector, testSelector,
               inputLinker = CaseLinker(), 
               actionTag = "plmDice", alwaysDo = False,
               session = None, additionalActionProps = None, scheduler = SimpleScheduler(), **singleActionParameters):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._refImages = refSelector.getSelection(self._session.artefacts)
    self._testImages = testSelector.getSelection(self._session.artefacts)
    
    self._inputLinker = inputLinker
    self._singleActionParameters = singleActionParameters

      
  def _generateActions(self):
    #filter only type result. Other artefact types are not interesting
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)
    
    refs = self.ensureRelevantArtefacts(self._refImages, resultSelector, "plm dice 1st input")
    tests = self.ensureRelevantArtefacts(self._testImages, resultSelector, "plm dice 2nd input")
    
    actions = list()
    
    for (pos,refImage) in enumerate(refs):
      linked2 = self._inputLinker.getLinkedSelection(pos,refs,tests)
           
      for lt in linked2:
        action = plmDiceAction(refImage, lt,
                            self._actionTag, alwaysDo = self._alwaysDo,
                            session = self._session,
                            additionalActionProps = self._additionalActionProps,
                            **self._singleActionParameters)
        actions.append(action)
    
    return actions
