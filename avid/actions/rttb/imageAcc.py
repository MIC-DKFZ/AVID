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

from avid.common import osChecker
from avid.splitter import BaseSplitter
from avid.actions import BatchActionBase
from avid.actions.cliActionBase import CLIActionBase
from avid.linkers import FractionLinker
from avid.selectors import TypeSelector
from avid.sorter import TimePointSorter
from avid.actions.simpleScheduler import SimpleScheduler
from avid.actions.rttb.doseMap import _getArtefactLoadStyle
from avid.externals.matchPoint import ensureMAPRegistrationArtefact

logger = logging.getLogger(__name__)

class ImageAccAction(CLIActionBase):
  '''Class that wraps the single action for the tool imageAcc.'''

  def __init__(self, images, registrations = None, weight = None,
               interpolator = "linear", operator="+",  outputExt = "nrrd",
               actionTag = "imageAcc", alwaysDo = False, session = None,
               additionalActionProps = None, actionConfig = None, propInheritanceDict = None, cli_connector = None):
    CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionID="doseAcc",
                           actionConfig = actionConfig, propInheritanceDict = propInheritanceDict, cli_connector = cli_connector)
    self._addInputArtefacts(images = images, registrations=registrations)
        
    self._images = self._ensureArtefacts(images, "images")

    if len(self._images)<2:
      raise RuntimeError('Cannot performe image accumulation. Need at least two image artefacts.')

    self._registrations = self._ensureArtefacts(registrations, "registrations")
    if self._registrations is not None:
      if len(self._registrations) == len(self._images):
        logger.info("Number of images ({}) equal the number of registrations. Assume that the first registration is"
                    " linked to the first image. This registration will therefore be skipped.".format(len(self._images)))
        self._registrations = self._registrations[1:]
      elif len(self._registrations)+1 == len(self._images):
        logger.info("Number of images ({}) exceeds the number of registrations ({}) by 1. Assume that the first"
                    " image has no registration. This registration will therefore be skipped.".format(len(self._images),
                                                                                                     len(self._registrations)))
      else:
        error ="Number of images ({}) does not fit to number of registrations ({}); registration count must either be" \
               " equal or smaller by 1 (assuming that first image is never mapped). Cannot performe action because" \
               " linking of the registrations to the images is unclear.".format(len(self._images),len(self._registrations))
        logger.error(error)
        raise RuntimeError(error)
    else:
      self._registrations = (len(self._images)-1)*[None]

    self._weight = weight
    if self._weight is not None:
      self._weight = 1 / len(self._images)

    self._interpolator = interpolator
    self._operator = operator
    self._outputExt = outputExt
    self._resultArtefact = None
    
    
  def _generateName(self):
    #need to define the outputs
    name = "imageAcc"

    if self._operator == "+":
      name += "_add_"
    elif self._operator == "*":
      name += "_multiply_"
    else:
      logger.error("operator %s not known.", self._operator)
      raise

    name += artefactHelper.getArtefactShortName(self._images[0])
    name += "to_"+artefactHelper.getArtefactShortName(self._images[-1])

    if self._registrations is not None:
      name += "_by_registration"
    else:
      name += "_by_identity"

    return name
   
  def _indicateOutputs(self):
    if self._resultArtefact is None:
      self._resultArtefact = self.generateArtefact(self._images[-1],
                                                   userDefinedProps={
                                                     artefactProps.TYPE: artefactProps.TYPE_VALUE_RESULT,
                                                     artefactProps.FORMAT: artefactProps.FORMAT_VALUE_ITK,
                                                     artefactProps.ACC_ELEMENT: str(len(self._images)-2)},
                                                   urlHumanPrefix=self.instanceName,
                                                   urlExtension=self._outputExt)

      self._interimArtefacts = list()
      for index, image in enumerate(self._images[1:-1]):
        self._interimArtefacts.append(self.generateArtefact(image,
                                       userDefinedProps={
                                         artefactProps.TYPE: artefactProps.TYPE_VALUE_INTERIM,
                                         artefactProps.FORMAT: artefactProps.FORMAT_VALUE_ITK,
                                         artefactProps.ACC_ELEMENT: str(index)},
                                       urlHumanPrefix=self.instanceName+"_interim_{}".format(index),
                                       urlExtension=self._outputExt))

    return [self._resultArtefact]

  def _generateCall(self, result, image1, image2, registration, weight1, weight2):
    resultPath = artefactHelper.getArtefactProperty(result, artefactProps.URL)
    image1Path = artefactHelper.getArtefactProperty(image1, artefactProps.URL)
    image2Path = artefactHelper.getArtefactProperty(image2, artefactProps.URL)
    registrationPath = artefactHelper.getArtefactProperty(registration, artefactProps.URL)

    result = ensureMAPRegistrationArtefact(registration, self.generateArtefact(image2), self._session)
    if result[0]:
      if result[1] is None:
        logger.error("Dose accumulation will fail. Given registration is not MatchPoint compatible and cannot be converted.")
      else:
        registrationPath = artefactHelper.getArtefactProperty(result[1], artefactProps.URL)
        logger.debug("Converted/Wrapped given registration artefact to be MatchPoint compatible. Wrapped artefact path: " + registrationPath)

    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])

    execURL = self._cli_connector.get_executable_url(self._session, "DoseAcc", self._actionConfig)

    content = '"'+execURL + '"' + ' "' + image1Path + '"' + ' "' + image2Path + '"' + ' "' + resultPath + '"'

    if registrationPath is not None:
      content += ' --registration "' + registrationPath + '"'

    if weight1 is not None:
      content += ' --weight1 "' + str(weight1) + '"'

    if weight2 is not None:
      content += ' --weight2 "' + str(weight2) + '"'

    content += ' --interpolator ' + self._interpolator

    content += ' --operator ' + self._operator

    content += ' --loadStyle1 ' + _getArtefactLoadStyle(image1)
    content += ' --loadStyle2 ' + _getArtefactLoadStyle(image2)

    return content

  def _prepareCLIExecution(self):
    resultArtefacts = self._interimArtefacts + [self._resultArtefact]
    image1Artefacts = [self._images[0]] + self._interimArtefacts
    weight2s = len(self._images)*[self._weight]
    weight1s = [self._weight] + len(self._interimArtefacts)*[1]

    content = ""

    for index,resultArtefact in enumerate(resultArtefacts):
      if not len(content) == 0:
        content += os.linesep
      line = self._generateCall(result=resultArtefact, image1=image1Artefacts[index], image2=self._images[index+1],
                                registration=self._registrations[index], weight1=weight1s[index], weight2=weight2s[index+1])
      content += line

    return content

class ImageAccBatchAction(BatchActionBase):    
  '''This action accumulates a whole selection of images and stores the result.'''
  
  def __init__(self,  imageSelector, registrationSelector = None, regLinker = None,
               imageSorter = None, imageSplitter = None, regSorter=None, regSplitter = None,
               actionTag = "imageAcc", session=None, additionalActionProps=None,
               scheduler = SimpleScheduler(), **singleActionParameters):

    if imageSorter is None:
      imageSorter = TimePointSorter()
    if imageSplitter is None:
      imageSplitter = BaseSplitter()

    if regSorter is None:
      regSorter = imageSorter
    if regSplitter is None:
      regSplitter = imageSplitter

    if regLinker is None:
      regLinker = FractionLinker(performInternalLinkage=True, allowOnlyFullLinkage=False)

    additionalInputSelectors = {"registrations": registrationSelector}
    linker = {"registrations": regLinker}
    sorter = {"images": imageSorter, "registrations": regSorter}
    splitter = {"images": imageSplitter, "registrations": regSplitter}

    BatchActionBase.__init__(self, actionTag= actionTag, actionClass=ImageAccAction, primaryInputSelector= imageSelector,
                             primaryAlias="images", additionalInputSelectors = additionalInputSelectors,
                             linker = linker, sorter=sorter, splitter=splitter, session= session,
                             relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                             scheduler=scheduler, additionalActionProps = additionalActionProps, **singleActionParameters)
