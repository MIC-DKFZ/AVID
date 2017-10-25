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


class CurveDescriptorMiniAppAction(CLIActionBase):
    '''Class that wrapps the single action for the tool CurveDescriptorMiniApp.'''

    def __init__(self, signal, mask = None, actionTag="CurveDescription", alwaysDo=False,
                 session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None):
        CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig=actionConfig,
                               propInheritanceDict=propInheritanceDict)

        self._addInputArtefacts(signal=signal, mask=mask)

        self._signal = signal
        self._mask = mask

        self._resultTemplate = self.generateArtefact(self._signal,
                                                     userDefinedProps={
                                                         artefactProps.TYPE: artefactProps.TYPE_VALUE_RESULT,
                                                         artefactProps.FORMAT: artefactProps.FORMAT_VALUE_ITK},
                                                     urlHumanPrefix=self.instanceName,
                                                     urlExtension='nrrd')

        if self._cwd is None:
            self._cwd = os.path.dirname(AVIDUrlLocater.getExecutableURL(self._session, "CurveDescriptorMiniApp", actionConfig))

    def _generateName(self):
        name = "curveDesc_{}".format(artefactHelper.getArtefactShortName(self._signal))
        if self._mask is not None:
            name += "_ROI_{}".format(artefactHelper.getArtefactShortName(self._mask))

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

        execURL = AVIDUrlLocater.getExecutableURL(self._session, "CurveDescriptorMiniApp", self._actionConfig)

        result = list()
        result.append(execURL)
        result.append('-i')
        result.append('{}'.format(signalPath))
        result.append('-o')
        result.append('{}'.format(resultPath))

        if maskPath is not None:
            result.append('-m')
            result.append('{}'.format(maskPath))

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


class CurveDescriptorMiniAppBatchAction(BatchActionBase):
    '''Batch action for CurveDescriptorMiniApp.'''

    def __init__(self, signalSelector, maskSelector=None, maskLinker = FractionLinker(),
                 actionTag="CurveDescription", alwaysDo=False, session=None,
                 additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
        BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

        self._signals = signalSelector.getSelection(self._session.artefacts)

        self._masks = list()
        if maskSelector is not None:
            self._masks = maskSelector.getSelection(self._session.artefacts)

        self._maskLinker = maskLinker

        self._singleActionParameters = singleActionParameters

    def _generateActions(self):
        # filter only type result. Other artefact types are not interesting
        resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)

        signals = self.ensureRelevantArtefacts(self._signals, resultSelector, "signals")
        masks = self.ensureRelevantArtefacts(self._masks, resultSelector, "masks")

        global logger

        actions = list()

        for (pos, signal) in enumerate(signals):
            linkedMasks = self._maskLinker.getLinkedSelection(pos, signals, masks)
            if len(linkedMasks) == 0:
                linkedMasks = [None]

            for lm in linkedMasks:
                action = CurveDescriptorMiniAppAction(signal, mask=lm,
                            actionTag=self._actionTag,
                            alwaysDo=self._alwaysDo,
                            session=self._session,
                            additionalActionProps=self._additionalActionProps,
                            **self._singleActionParameters)
                actions.append(action)

        return actions
