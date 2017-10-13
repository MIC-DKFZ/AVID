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
from avid.selectors import TypeSelector
from simpleScheduler import SimpleScheduler
from avid.selectors.keyValueSelector import FormatSelector

logger = logging.getLogger(__name__)


class MRPerfusionMiniAppAction(CLIActionBase):
    '''Class that wrapps the single action for the tool MRPerfusionMiniApp.'''
    MODEL_DESCRIPTIVE = "descriptive"
    MODEL_TOFTS = "tofts"
    MODEL_2CX = "2CX"

    def __init__(self, signal, model=MODEL_TOFTS, injectiontime=None, aifmask = None, aifimage = None , hematocrit=0.45,
                 roibased=False, mask = None, constraints = False, actionTag="MRPerfusion", alwaysDo=False,
                 session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None):
        CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig=actionConfig,
                               propInheritanceDict=propInheritanceDict)
        self._addInputArtefacts(signal=signal)

        self._signal = signal
        self._model = model
        self._injectiontime = injectiontime
        self._aifmask = aifmask
        self._aifimage = aifimage
        self._hematocrit = hematocrit
        self._roibased = roibased
        self._mask = mask
        self._constraints = constraints

    if aifimage is not None and aifmask is not None:
        raise RuntimeError("Cannot use an AIF image without and AIF mask. Please specify mask.")

    def _generateName(self):
        style = ''
        if not self._roibased:
            style = 'pixel'
        name = "perfusion_{}_{}_#".format(style, str(artefactHelper.getArtefactProperty(self._signal, artefactProps.ACTIONTAG)),
                                          str(artefactHelper.getArtefactProperty(self._signal, artefactProps.TIMEPOINT)))
        if self._mask is not None:
            name += "_ROI_{}_#{}".format(str(artefactHelper.getArtefactProperty(self._mask, artefactProps.ACTIONTAG)),
                                          str(artefactHelper.getArtefactProperty(self._mask, artefactProps.TIMEPOINT)))
        if self._aifimage is not None:
            name += "_AIF_{}_#{}".format(str(artefactHelper.getArtefactProperty(self._aifimage, artefactProps.ACTIONTAG)),
                                          str(artefactHelper.getArtefactProperty(self._aifimage, artefactProps.TIMEPOINT)))
        if self._aifmask is not None:
            name += "_AIFROI_{}_#{}".format(str(artefactHelper.getArtefactProperty(self._aifmask, artefactProps.ACTIONTAG)),
                                          str(artefactHelper.getArtefactProperty(self._aifmask, artefactProps.TIMEPOINT)))

        return name

    def _indicateOutputs(self):
        self._resultArtefact = self.generateArtefact(self._signal,
                                                     userDefinedProps={
                                                         artefactProps.TYPE: artefactProps.TYPE_VALUE_RESULT,
                                                         artefactProps.FORMAT: artefactProps.FORMAT_VALUE_ITK},
                                                     urlHumanPrefix=self.instanceName,
                                                     urlExtension='nrrd')
        return [self._resultArtefact]

    def _prepareCLIExecution(self):
        resultPath = artefactHelper.getArtefactProperty(self._resultArtefact, artefactProps.URL)
        signalPath = artefactHelper.getArtefactProperty(self._signal, artefactProps.URL)

        osChecker.checkAndCreateDir(os.path.split(resultPath)[0])

        execURL = AVIDUrlLocater.getExecutableURL(self._session, "MR2SignalConcentrationMiniApp", self._actionConfig)


        content = '"{}" -i "{}" -o "{}"'.format(execURL, signalPath, resultPath)
        if (self._conversiontype is self.CONVERSION_T1_ABSOLUTE or self._conversiontype is self.CONVERSION_T1_RELATIVE)
            content += ' -k "{}" '.format(self._k)
        elif (self._conversiontype is self.CONVERSION_T1_FLASH)
            content += ' -k "{}" --TE "{}"'.format(self._k)
        elif (self._conversiontype is self.CONVERSION_T2)
            content += ' --relaxivity "{}" --recovery-time "{}" --relaxation-time "{}"'.format(self._relaxivity, self._recoveryTime, self._relaxationTime)

        return content


class MRPerfusionMiniAppBatchAction(BatchActionBase):
    '''Batch action for MRPerfusionMiniApp.'''

    def __init__(self, signalSelector,
                 actionTag="MR2SignalConcentration", alwaysDo=False, session=None,
                 additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
        BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

        self._signals = signalSelector.getSelection(self._session.artefacts)

        self._singleActionParameters = singleActionParameters

    def _generateActions(self):
        # filter only type result. Other artefact types are not interesting
        resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)

        signals = self.ensureRelevantArtefacts(self._signals, resultSelector, "signals")

        actions = list()

        for (pos, signal) in enumerate(signals):
            action = MR2SignalConcentrationMiniAppAction(signal,
                                    actionTag=self._actionTag,
                                    alwaysDo=self._alwaysDo,
                                    session=self._session,
                                    additionalActionProps=self._additionalActionProps,
                                    **self._singleActionParameters)
            actions.append(action)

        return actions
