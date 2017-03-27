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
from avid.linkers import CaseLinker
from avid.selectors import TypeSelector
from simpleScheduler import SimpleScheduler
from avid.externals.plastimatch import parseCompareResult
from avid.externals.doseTool import saveSimpleDictAsResultXML

logger = logging.getLogger(__name__)

class plmCompareAction(CLIActionBase):
  '''Class that wraps the single action for the tool mapR.'''

  def __init__(self, refImage, testImage, 
               actionTag = "plmCompare", alwaysDo = False, 
               session = None, additionalActionProps = None, actionConfig = None, propInheritanceDict = dict()):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig=actionConfig,
                           propInheritanceDict=propInheritanceDict)
    self._addInputArtefacts(refImage = refImage, testImage = testImage)
    self._refImage = refImage
    self._testImage = testImage
    
    cwd = os.path.dirname(AVIDUrlLocater.getExecutableURL(self._session, "plastimatch", actionConfig))
    self._cwd = cwd    
    
  def _generateName(self):
    name = "plmCompare_"+str(artefactHelper.getArtefactProperty(self._refImage,artefactProps.ACTIONTAG))

    objective = artefactHelper.getArtefactProperty(self._refImage, artefactProps.OBJECTIVE)
    if not objective is None:
      name += '-%s' % objective

    name += "_#" + str(artefactHelper.getArtefactProperty(self._refImage, artefactProps.TIMEPOINT)) \
            + "_vs_" + str(artefactHelper.getArtefactProperty(self._testImage, artefactProps.ACTIONTAG))

    objective = artefactHelper.getArtefactProperty(self._testImage, artefactProps.OBJECTIVE)
    if not objective is None:
      name += '-%s' % objective

    name += "_#" + str(artefactHelper.getArtefactProperty(self._testImage, artefactProps.TIMEPOINT))
    return name
   
  def _indicateOutputs(self):

    self._resultArtefact = self.generateArtefact(self._testImage,
                                                 userDefinedProps={artefactProps.TYPE:artefactProps.TYPE_VALUE_RESULT,
                                                                   artefactProps.FORMAT: artefactProps.FORMAT_VALUE_RTTB_STATS_XML},
                                                 urlHumanPrefix=self.instanceName,
                                                 urlExtension='xml')

    return [self._resultArtefact]

      
  def _prepareCLIExecution(self):
    
    inputPath = artefactHelper.getArtefactProperty(self._refImage,artefactProps.URL)
    input2Path = artefactHelper.getArtefactProperty(self._testImage,artefactProps.URL)

    execURL = AVIDUrlLocater.getExecutableURL(self._session, "plastimatch", self._actionConfig)
    
    content = '"' + execURL + '" compare ' + ' "' + inputPath + '"' + ' "' + input2Path +'"'

    return content


  def _postProcessCLIExecution(self):

    resultPath = artefactHelper.getArtefactProperty(self._resultArtefact,artefactProps.URL)
    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])

    result = parseCompareResult(open(self._logFilePath).read())

    saveSimpleDictAsResultXML(result, resultPath)


class plmCompareBatchAction(BatchActionBase):    
  '''Base class for action objects that are used together with selectors and
    should therefore able to process a batch of SingleActionBased actions.'''
  
  def __init__(self,  refSelector, testSelector,
               inputLinker = CaseLinker(), 
               actionTag = "plmCompare", alwaysDo = False,
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
        action = plmCompareAction(refImage, lt,
                            self._actionTag, alwaysDo = self._alwaysDo,
                            session = self._session,
                            additionalActionProps = self._additionalActionProps,
                            **self._singleActionParameters)
        actions.append(action)

    return actions

