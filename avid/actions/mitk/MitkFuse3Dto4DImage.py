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

import os
import logging
import subprocess

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper
import re

from avid.common import osChecker, AVIDUrlLocater
from avid.linkers import CaseLinker
from avid.linkers import FractionLinker
from avid.sorter import BaseSorter, KeyValueSorter
from avid.splitter import BaseSplitter, KeyValueSplitter

from avid.actions import BatchActionBase
from avid.actions.cliActionBase import CLIActionBase
from avid.selectors import TypeSelector
from avid.actions.simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)


class MitkFuse3Dto4DImageAction(CLIActionBase):
    '''Class that wrapps the single action for the tool MitkFuse3Dto4DImage.'''

    def __init__(self, images, timeProperty = None, timeGenerationCallable = None, actionTag="MitkFuse3Dto4DImage", alwaysDo=False,
                 session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None, cli_connector=None):
        CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig=actionConfig,
                               propInheritanceDict=propInheritanceDict, cli_connector=cli_connector)

        self._images = {}
        if timeGenerationCallable is not None:
            for image in images:
                self._images[timeGenerationCallable(image)] = image
        elif timeProperty is not None:
            for image in images:
                self._images[int(artefactHelper.getArtefactProperty(image, timeProperty))] = image
        else:
            raise RuntimeError('Cannot initiate MitkFuse3Dto4DImageAction. Either "timeProperty" or'
                               ' "timeGenerationCallable" must be defined, but both are None.')

        self._addInputArtefacts(images=images)

        if self._cwd is None:
            self._cwd = os.path.dirname(AVIDUrlLocater.getExecutableURL(self._session, "MitkFuse3Dto4DImage", actionConfig))


    def _getFirstImageKey(self):
        return next(iter(self._images.keys()))


    def _generateName(self):
        name = "Fused"
        name += "_{}".format(artefactHelper.getArtefactShortName(self._images[self._getFirstImageKey()]))
        for time in self._images:
            name += "_{}".format(time)

        return name

    def _indicateOutputs(self):
        # Specify result artefact
        self._resultArtefact = self.generateArtefact(self._images[self._getFirstImageKey()],
                                                        userDefinedProps={artefactProps.TYPE:artefactProps.TYPE_VALUE_RESULT,
                                                        artefactProps.FORMAT:artefactProps.FORMAT_VALUE_ITK},
                                                        urlHumanPrefix=self.instanceName,urlExtension='nrrd')

        return [self._resultArtefact]

    def _generateTimeInformation(self):
        times = list(self._images.keys())

        result = '{}'.format(times[0])
        for time in times[1:]:
            result += ' {}'.format(time)
        result += ' {}'.format(times[-1]*2)
        return result

    def _generateInputInformation(self):
        result = ''
        for time in self._images:
            imagePath = artefactHelper.getArtefactProperty(self._images[time], artefactProps.URL)
            result += ' "{}"'.format(imagePath)
        return result

    def _prepareCLIExecution(self):

        resultPath = artefactHelper.getArtefactProperty(self._resultArtefact, artefactProps.URL)
        osChecker.checkAndCreateDir(os.path.split(resultPath)[0])

        content = ""

        try:
            execURL = self._cli_connector.get_executable_url(self._session, "MitkFuse3Dto4DImage", self._actionConfig)

            content += '"{}" -i{} -o "{}" -t {}'.format(execURL, self._generateInputInformation(), resultPath, self._generateTimeInformation())
        except:
            logger.error("Error for getExecutable.")
            raise

        return content


class MitkFuse3Dto4DImageBatchAction(BatchActionBase):
    '''Batch action for MitkFuse3Dto4DImage that produces a fused 4D image.
        @param splitProperties You can define a list of split properties (list of property names)
        to separate images. All artefacts of one action will be fused into one 4D image.'''

    def __init__(self, imageSelector, timeProperty = None, splitProperties = None,
                 actionTag="MitkFuse3Dto4DImage", session=None,
                 additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):

        sorter = {BatchActionBase.PRIMARY_INPUT_KEY: BaseSorter()}
        if timeProperty is not None:
            sorter = {BatchActionBase.PRIMARY_INPUT_KEY: KeyValueSorter(key=timeProperty, asNumbers=True)}

        splitter = {BatchActionBase.PRIMARY_INPUT_KEY: BaseSplitter()}
        if splitProperties is not None:
            splitter = {BatchActionBase.PRIMARY_INPUT_KEY: KeyValueSplitter(*splitProperties)}

        BatchActionBase.__init__(self, actionTag=actionTag, actionClass=MitkFuse3Dto4DImageAction,
                                 primaryInputSelector=imageSelector,
                                 primaryAlias="images", splitter=splitter, sorter=sorter, session=session,
                                 relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps=additionalActionProps,
                                 timeProperty=timeProperty, **singleActionParameters)
