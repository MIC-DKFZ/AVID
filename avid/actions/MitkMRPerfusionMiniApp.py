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
import re
import subprocess

import avid.common.artefact as artefactHelper
import avid.common.artefact.defaultProps as artefactProps
from avid.common import osChecker, AVIDUrlLocater
from avid.linkers import FractionLinker
from avid.selectors import TypeSelector
from . import BatchActionBase
from .cliActionBase import CLIActionBase
from .simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)


class MitkMRPerfusionMiniAppAction(CLIActionBase):
    """Class that wrapps the single action for the tool MRPerfusionMiniApp."""
    MODEL_DESCRIPTIVE = "descriptive"
    MODEL_TOFTS = "tofts"
    MODEL_2CX = "2CX"
    MODEL_3SL = "3SL"
    MODEL_2SL = "2SL"

    def __init__(self, signal, model=MODEL_TOFTS, injectiontime=None, mask=None, aifmask=None, aifimage=None,
                 hematocrit=0.45, roibased=False, constraints=False, actionTag="MRPerfusion", alwaysDo=False,
                 session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None, cli_connector=None):
        CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps,
                               actionID="MitkMRPerfusionMiniApp", actionConfig=actionConfig,
                               propInheritanceDict=propInheritanceDict, cli_connector=cli_connector)

        if aifimage is not None and aifmask is None:
            raise RuntimeError("Cannot use an AIF image without and AIF mask. Please specify mask.")

        self._addInputArtefacts(signal=signal, mask=mask, aifmask=aifmask, aifimage=aifimage)

        self._signal = self._ensureSingleArtefact(signal, "signal")
        self._model = model
        self._injectiontime = injectiontime
        self._aifmask = self._ensureSingleArtefact(aifmask, "aifmask")
        self._aifimage = self._ensureSingleArtefact(aifimage, "aifimage")
        self._hematocrit = hematocrit
        self._roibased = roibased
        self._mask = self._ensureSingleArtefact(mask, "mask")
        self._constraints = constraints

        self._resultTemplate = self.generateArtefact(self._signal,
                                                     userDefinedProps={
                                                         artefactProps.TYPE: artefactProps.TYPE_VALUE_RESULT,
                                                         artefactProps.FORMAT: artefactProps.FORMAT_VALUE_ITK},
                                                     urlHumanPrefix=self.instanceName,
                                                     urlExtension='nrrd')

    def _generateName(self):
        style = ''
        if not self._roibased:
            style = 'pixel'
        name = "perfusion_{}_{}_{}".format(self._model, style, artefactHelper.getArtefactShortName(self._signal))
        if self._mask is not None:
            name += "_ROI_{}".format(artefactHelper.getArtefactShortName(self._mask))
        if self._aifimage is not None:
            name += "_AIF_{}".format(artefactHelper.getArtefactShortName(self._aifimage))
        if self._aifmask is not None:
            name += "_AIFROI_{}".format(artefactHelper.getArtefactShortName(self._aifmask))

        return name

    def _indicateOutputs(self):
        resultsInfo = self._previewResult()

        self._resultArtefacts = dict()
        for info in resultsInfo:
            result = self.generateArtefact(self._signal,
                                           userDefinedProps={
                                               artefactProps.TYPE: artefactProps.TYPE_VALUE_RESULT,
                                               artefactProps.FORMAT: artefactProps.FORMAT_VALUE_ITK,
                                               artefactProps.RESULT_SUB_TAG: info[1]})
            result[artefactProps.URL] = info[2]
            self._resultArtefacts[info[1]] = result

        return list(self._resultArtefacts.values())

    def _generateCLIArguments(self):
        resultPath = artefactHelper.getArtefactProperty(self._resultTemplate, artefactProps.URL)
        signalPath = artefactHelper.getArtefactProperty(self._signal, artefactProps.URL)
        maskPath = artefactHelper.getArtefactProperty(self._mask, artefactProps.URL)
        aifMaskPath = artefactHelper.getArtefactProperty(self._aifmask, artefactProps.URL)
        aifPath = artefactHelper.getArtefactProperty(self._aifimage, artefactProps.URL)

        execURL = self._cli_connector.get_executable_url(self._session, self._actionID, self._actionConfig)

        result = list()
        result.append(execURL)
        result.append('-i')
        result.append('{}'.format(signalPath))
        result.append('-o')
        result.append('{}'.format(resultPath))
        result.append('--model')
        result.append('{}'.format(self._model))

        if maskPath is not None:
            result.append('-m')
            result.append('{}'.format(maskPath))

        if aifMaskPath is not None:
            result.append('--aifmask')
            result.append('{}'.format(aifMaskPath))

        if aifPath is not None:
            result.append('--aifimage')
            result.append('{}'.format(aifPath))

        if self._roibased:
            result.append('-r')

        if self._constraints:
            result.append('-c')

        if self._model == self.MODEL_DESCRIPTIVE and self._injectiontime is not None:
            result.append('--injectiontime')
            result.append('{}'.format(self._injectiontime))

        if not self._model == self.MODEL_DESCRIPTIVE or not self._model == self.MODEL_2SL \
                or not self._model == self.MODEL_3SL:
            result.append('--hematocrit')
            result.append('{}'.format(self._hematocrit))

        return result

    def _previewResult(self):
        """Helper function that call the MiniApp in preview mode to depict the results. Returns a list of trippels (type, name, url)."""
        results = list()
        try:
            args = self._generateCLIArguments()
            args.append('--preview')
            output = subprocess.check_output(args, cwd=self._cwd)

            for line in output.splitlines():
                stringLine = line.decode()
                if stringLine.startswith('Store result '):
                    regResults = re.findall('Store result (.*): (.*) -> (.*)', stringLine)

                    try:
                        paramtype = regResults[0][0]
                        name = regResults[0][1]
                        url = regResults[0][2]
                        results.append((paramtype, name, url))
                    except:
                        raise RuntimeError('Failed to parse storage info line: {}'.format(stringLine))

        except subprocess.CalledProcessError:
            pass

        return results

    def _prepareCLIExecution(self):
        args = self._generateCLIArguments()
        # escape everything to be sure that no propblem in the batch file (reserved charactars) or with the pathes occure.
        # cannot be done in _generateCLIArguments because the direct call used by preview does not like the escapation.
        # should be handled soundly by reworking prepareCLIExecution not returning the content string, but all arguments
        # of the call. Then escaption etc can be handled in the base class.
        content = args[0] + ' "' + '" "'.join(args[1:]) + '"'
        resultPath = artefactHelper.getArtefactProperty(self._resultTemplate, artefactProps.URL)
        osChecker.checkAndCreateDir(os.path.split(resultPath)[0])

        return content


class MitkMRPerfusionMiniAppBatchAction(BatchActionBase):
    """Batch action for MRPerfusionMiniApp."""

    MODEL_DESCRIPTIVE = MitkMRPerfusionMiniAppAction.MODEL_DESCRIPTIVE
    MODEL_TOFTS = MitkMRPerfusionMiniAppAction.MODEL_TOFTS
    MODEL_2CX = MitkMRPerfusionMiniAppAction.MODEL_2CX
    MODEL_2SL = MitkMRPerfusionMiniAppAction.MODEL_2SL
    MODEL_3SL = MitkMRPerfusionMiniAppAction.MODEL_3SL

    def __init__(self, signalSelector, maskSelector=None, aifmaskSelector=None, aifSelector=None,
                 maskLinker=None, aifLinker=None, aifmaskLinker=None,
                 actionTag="MRPerfusion", session=None,
                 additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):

        if maskLinker is None:
            maskLinker = FractionLinker()
        if aifLinker is None:
            aifLinker = FractionLinker()
        if aifmaskLinker is None:
            aifmaskLinker = FractionLinker()

        additionalInputSelectors = {"mask": maskSelector, "aifmask": aifmaskSelector,
                                    "aifimage": aifSelector}
        linker = {"mask": maskLinker, "aifmask": aifmaskLinker,
                  "aifimage": aifLinker}

        BatchActionBase.__init__(self, actionTag=actionTag, actionClass=MitkMRPerfusionMiniAppAction,
                                 primaryInputSelector=signalSelector,
                                 primaryAlias="signal", additionalInputSelectors=additionalInputSelectors,
                                 linker=linker, session=session,
                                 relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps=additionalActionProps,
                                 **singleActionParameters)
