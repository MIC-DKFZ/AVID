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
from avid.linkers import FractionLinker
import avid.common.demultiplexer as demux

from . import BatchActionBase
from .cliActionBase import CLIActionBase
from avid.selectors import TypeSelector
from .simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)


def _defaultGetCaption(workflowArtefact):
    '''Default strategy for the short name. If no objective is defined '''
    tag = artefactHelper.getArtefactProperty(workflowArtefact, artefactProps.ACTIONTAG)
    timePoint = artefactHelper.getArtefactProperty(workflowArtefact, artefactProps.TIMEPOINT)

    objective = artefactHelper.getArtefactProperty(workflowArtefact, artefactProps.OBJECTIVE)
    sub_result = artefactHelper.getArtefactProperty(workflowArtefact, artefactProps.RESULT_SUB_TAG)
    additionalInfo = ''
    if not objective is None:
        additionalInfo = '-{}'.format(objective)

    if not sub_result is None:
        additionalInfo = '{}-{}'.format(additionalInfo,sub_result)

    name = '{}{}#{}'.format(tag, additionalInfo, timePoint)

    return name


class PixelDumpMiniAppAction(CLIActionBase):
    '''Class that wrapps the single action for the tool PixelDumpMiniApp.'''

    def __init__(self, signals, mask=None, captionDelegate=None, actionTag="PixelDump", alwaysDo=False,
                 session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None):
        CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig=actionConfig,
                               propInheritanceDict=propInheritanceDict)

        self._signals = dict()

        for pos, artefact in enumerate(signals):
            self._signals['input_{}'.format(pos)] = artefact

        self._mask = mask

        tempInput = self._signals.copy()
        tempInput['mask'] = mask
        self._addInputArtefacts(**tempInput)

        self._captionDelegate = captionDelegate
        if captionDelegate is None:
            self._captionDelegate = _defaultGetCaption

        if self._cwd is None:
            self._cwd = os.path.dirname(AVIDUrlLocater.getExecutableURL(self._session, "PixelDumpMiniApp", actionConfig))

    def _firstSignal(self):
        return self._signals[sorted(self._signals.keys())[0]]

    def _lastSignal(self):
        return self._signals[sorted(self._signals.keys())[-1]]

    def _generateName(self):
        name = "dump_{}_to_{}".format(artefactHelper.getArtefactShortName(self._firstSignal()), artefactHelper.getArtefactShortName(self._lastSignal()))
        if self._mask is not None:
            name += "_ROI_{}".format(artefactHelper.getArtefactShortName(self._mask))

        return name

    def _indicateOutputs(self):
        self._resultArtefact = self.generateArtefact(self._firstSignal(),
                                                     userDefinedProps={
                                                         artefactProps.TYPE: artefactProps.TYPE_VALUE_RESULT,
                                                         artefactProps.FORMAT: artefactProps.FORMAT_VALUE_CSV},
                                                     urlHumanPrefix=self.instanceName,
                                                     urlExtension='csv')
        return [self._resultArtefact]

    def _generateCLIArguments(self):
        resultPath = artefactHelper.getArtefactProperty(self._resultArtefact, artefactProps.URL)
        maskPath = artefactHelper.getArtefactProperty(self._mask, artefactProps.URL)

        signalPathes = list()
        captions = list()
        for signalname in self._signals:
            signalPathes.append(artefactHelper.getArtefactProperty(self._signals[signalname], artefactProps.URL))
            captions.append(self._captionDelegate(self._signals[signalname]))

        execURL = self._cli_connector.get_executable_url(self._session, "PixelDumpMiniApp", self._actionConfig)

        result = list()
        result.append(execURL)
        result.append('-i')
        for path in signalPathes:
            result.append('"{}"'.format(path))
        result.append('-o')
        result.append('"{}"'.format(resultPath))
        result.append('-c')
        for caption in captions:
            result.append('"{}"'.format(caption))

        if maskPath is not None:
            result.append('-m')
            result.append('"{}"'.format(maskPath))

        return result

    def _prepareCLIExecution(self):
        content = ' '.join(self._generateCLIArguments())
        resultPath = artefactHelper.getArtefactProperty(self._resultArtefact, artefactProps.URL)
        osChecker.checkAndCreateDir(os.path.split(resultPath)[0])

        return content


class PixelDumpMiniAppBatchAction(BatchActionBase):
    '''Batch action for PixelDumpMiniApp.'''

    def __init__(self, signalSelector, maskSelector=None, maskLinker = FractionLinker(), splitProperties = None,
                 actionTag = "PixelDump", alwaysDo=False, session = None,
                 additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
        '''@param splitProperty String specifying a property name. If specified this property will be used to split the
        signals into specific jobs.'''
        BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

        self._signals = signalSelector.getSelection(self._session.artefacts)

        self._masks = list()
        if maskSelector is not None:
            self._masks = maskSelector.getSelection(self._session.artefacts)

        self._maskLinker = maskLinker
        self._splitProperties = splitProperties

        self._singleActionParameters = singleActionParameters

    def _generateActions(self):
        # filter only type result. Other artefact types are not interesting

        resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)

        allsignals = self.ensureRelevantArtefacts(self._signals, resultSelector, "signals")
        masks = self.ensureRelevantArtefacts(self._masks, resultSelector, "masks")

        global logger

        splittedSignals = [allsignals]

        if self._splitProperties is not None:
            splittedSignals = demux.splitArtefact(allsignals, *self._splitProperties)

        actions = list()

        for signals in splittedSignals:
            linkedMasks = self._maskLinker.getLinkedSelection(0, signals, masks)
            if len(linkedMasks) == 0:
                linkedMasks = [None]

            for lm in linkedMasks:
                action = PixelDumpMiniAppAction(signals=signals, mask=lm,
                                                actionTag=self._actionTag, alwaysDo=self._alwaysDo, session=self._session,
                                                additionalActionProps=self._additionalActionProps,
                                                **self._singleActionParameters)
                actions.append(action)

        return actions
