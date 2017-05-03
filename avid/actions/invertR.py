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
from simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)


class invertRAction(CLIActionBase):
  '''Class that wrapps the single action for the tool invertR.'''

  def __init__(self, registration, templateImage=None, directMapping=False, inverseMapping=False, actionTag="invertR", alwaysDo=False,
               session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=dict()):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig=actionConfig,
                           propInheritanceDict=propInheritanceDict)
    self._addInputArtefacts(registration=registration, templateImage=templateImage)

    self._registration = registration
    self._templateImage = templateImage
    self._directMapping = directMapping
    self._inverseMapping = inverseMapping

    cwd = os.path.dirname(AVIDUrlLocater.getExecutableURL(self._session, "invertR", actionConfig))
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

    name = self._generateName()

    # Specify result artefact
    self._resultArtefact = self.generateArtefact(artefactRef)
    self._resultArtefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
    self._resultArtefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_MATCHPOINT

    path = artefactHelper.generateArtefactPath(self._session, self._resultArtefact)
    resName = name + "." + str(artefactHelper.getArtefactProperty(self._resultArtefact, artefactProps.ID)) + os.extsep + "mapr"
    resName = os.path.join(path, resName)

    self._resultArtefact[artefactProps.URL] = resName

    return [self._resultArtefact]

  def _prepareCLIExecution(self):
    resultPath = artefactHelper.getArtefactProperty(self._resultArtefact, artefactProps.URL)

    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])

    try:
      execURL = AVIDUrlLocater.getExecutableURL(self._session, "invertR", self._actionConfig)
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
