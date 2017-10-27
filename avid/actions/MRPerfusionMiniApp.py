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
import subprocess

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper
import re

from avid.common import osChecker, AVIDUrlLocater
from avid.linkers import CaseLinker
from avid.linkers import FractionLinker

from . import BatchActionBase
from cliActionBase import CLIActionBase
from avid.selectors import TypeSelector
from simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)


class MRPerfusionMiniAppAction(CLIActionBase):
    '''Class that wrapps the single action for the tool MRPerfusionMiniApp.'''
    MODEL_DESCRIPTIVE = "descriptive"
    MODEL_TOFTS = "tofts"
    MODEL_2CX = "2CX"

    def __init__(self, signal, model=MODEL_TOFTS, injectiontime=None, mask = None, aifmask = None, aifimage = None,
                 hematocrit=0.45, roibased=False, constraints = False, actionTag="MRPerfusion", alwaysDo=False,
                 session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None):
        CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig=actionConfig,
                               propInheritanceDict=propInheritanceDict)

        if aifimage is not None and aifmask is None:
            raise RuntimeError("Cannot use an AIF image without and AIF mask. Please specify mask.")

        self._addInputArtefacts(signal=signal, mask = mask, aifmask = aifmask, aifimage = aifimage)

        self._signal = signal
        self._model = model
        self._injectiontime = injectiontime
        self._aifmask = aifmask
        self._aifimage = aifimage
        self._hematocrit = hematocrit
        self._roibased = roibased
        self._mask = mask
        self._constraints = constraints

        self._resultTemplate = self.generateArtefact(self._signal,
                                                     userDefinedProps={
                                                         artefactProps.TYPE: artefactProps.TYPE_VALUE_RESULT,
                                                         artefactProps.FORMAT: artefactProps.FORMAT_VALUE_ITK},
                                                     urlHumanPrefix=self.instanceName,
                                                     urlExtension='nrrd')

        if self._cwd is None:
            self._cwd = os.path.dirname(AVIDUrlLocater.getExecutableURL(self._session, "MRPerfusionMiniApp", actionConfig))

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

        return self._resultArtefacts.values()

    def _generateCLIArguments(self):
        resultPath = artefactHelper.getArtefactProperty(self._resultTemplate, artefactProps.URL)
        signalPath = artefactHelper.getArtefactProperty(self._signal, artefactProps.URL)
        maskPath = artefactHelper.getArtefactProperty(self._mask, artefactProps.URL)
        aifMaskPath = artefactHelper.getArtefactProperty(self._aifmask, artefactProps.URL)
        aifPath = artefactHelper.getArtefactProperty(self._aifimage, artefactProps.URL)

        execURL = AVIDUrlLocater.getExecutableURL(self._session, "MRPerfusionMiniApp", self._actionConfig)

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

        if not self._model == self.MODEL_DESCRIPTIVE:
            result.append('--hematocrit')
            result.append('{}'.format(self._hematocrit))

        return result

    def _previewResult(self):
        '''Helper function that call the MiniApp in preview mode to depict the results. Returns a list of trippels (type, name, url).'''
        results = list()
        try:
            args = self._generateCLIArguments()
            args.append('--preview')
            output = subprocess.check_output(args, cwd=self._cwd)

            for line in output.splitlines():
                if line.startswith('Store result '):
                    regResults = re.findall('Store result (.*): (.*) -> (.*)', line)

                    try:
                        type = regResults[0][0]
                        name = regResults[0][1]
                        url = regResults[0][2]
                        results.append((type,name,url))
                    except:
                        raise RuntimeError('Failed to parse storage info line: {}'.format(line))

        except subprocess.CalledProcessError as err:
            pass

        return results


    def _prepareCLIExecution(self):
        content = ' '.join(self._generateCLIArguments())
        resultPath = artefactHelper.getArtefactProperty(self._resultTemplate, artefactProps.URL)
        osChecker.checkAndCreateDir(os.path.split(resultPath)[0])

        return content


class MRPerfusionMiniAppBatchAction(BatchActionBase):
    '''Batch action for MRPerfusionMiniApp.'''

    MODEL_DESCRIPTIVE = MRPerfusionMiniAppAction.MODEL_DESCRIPTIVE
    MODEL_TOFTS = MRPerfusionMiniAppAction.MODEL_TOFTS
    MODEL_2CX = MRPerfusionMiniAppAction.MODEL_2CX

    def __init__(self, signalSelector, maskSelector=None, aifMaskSelector = None, aifSelector = None,
                 maskLinker = FractionLinker(), aifLinker = FractionLinker(), aifMaskLinker = FractionLinker(),
                 actionTag="MRPerfusion", alwaysDo=False, session=None,
                 additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
        BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

        self._signals = signalSelector.getSelection(self._session.artefacts)

        self._masks = list()
        if maskSelector is not None:
            self._masks = maskSelector.getSelection(self._session.artefacts)
        self._aifs = list()
        if aifSelector is not None:
            self._aifs = aifSelector.getSelection(self._session.artefacts)
        self._aifmasks = list()
        if aifMaskSelector is not None:
            self._aifmasks = aifMaskSelector.getSelection(self._session.artefacts)

        self._maskLinker = maskLinker
        self._aifLinker = aifLinker
        self._aifMaskLinker = aifMaskLinker

        self._singleActionParameters = singleActionParameters

    def _generateActions(self):
        # filter only type result. Other artefact types are not interesting
        resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)

        signals = self.ensureRelevantArtefacts(self._signals, resultSelector, "signals")
        masks = self.ensureRelevantArtefacts(self._masks, resultSelector, "masks")
        aifs = self.ensureRelevantArtefacts(self._aifs, resultSelector, "aifs")
        aifmasks = self.ensureRelevantArtefacts(self._aifmasks, resultSelector, "aifmasks")

        global logger

        actions = list()

        for (pos, signal) in enumerate(signals):
            linkedMasks = self._maskLinker.getLinkedSelection(pos, signals, masks)
            if len(linkedMasks) == 0:
                linkedMasks = [None]

            linkedAIFs = self._aifLinker.getLinkedSelection(pos, signals, aifs)
            if len(linkedAIFs) == 0:
                linkedAIFs = [None]

            linkedAIFMasks = self._aifMaskLinker.getLinkedSelection(pos, signals, aifmasks)
            if len(linkedAIFMasks) == 0:
                linkedAIFMasks = [None]

            for lm in linkedMasks:
                for lam in linkedAIFMasks:
                    for la in linkedAIFs:
                        action = MRPerfusionMiniAppAction(signal, mask=lm, aifimage=la, aifmask=lam,
                                    actionTag=self._actionTag,
                                    alwaysDo=self._alwaysDo,
                                    session=self._session,
                                    additionalActionProps=self._additionalActionProps,
                                    **self._singleActionParameters)
                        actions.append(action)

        return actions
