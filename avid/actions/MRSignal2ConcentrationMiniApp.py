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

logger = logging.getLogger(__name__)


class MR2SignalConcentrationMiniAppAction(CLIActionBase):
    '''Class that wrapps the single action for the tool MR2SignalConcentrationMiniApp.'''
    CONVERSION_T1_ABSOLUTE = "t1-absolute"
    CONVERSION_T1_RELATIVE = "t1-relative"
    CONVERSION_T1_FLASH = "t1-flash"
    CONVERSION_T2 = "t2"

    def __init__(self, signal, conversiontype=CONVERSION_T1_ABSOLUTE, k=1, recoveryTime=None,
                 relaxivity=None, relaxationTime=None, te=None, actionTag="MRSignal2Concentration", alwaysDo=False,
                 session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None):
        CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, actionConfig=actionConfig,
                               propInheritanceDict=propInheritanceDict)
        self._addInputArtefacts(signal=signal)

        self._signal = signal
        self._conversiontype = conversiontype
        self._k = k
        self._recoveryTime = recoveryTime
        self._relaxivity = relaxivity
        self._relaxationTime = relaxationTime
        self._te = te

        if te is None and conversiontype == self.CONVERSION_T2:
            raise RuntimeError("Cannot convert T2 without parameter TE set.")
        if conversiontype == self.CONVERSION_T1_FLASH and (recoveryTime is None or relaxationTime is None or relaxivity is None):
            raise RuntimeError("Cannot convert T1 flash without parameter recoveryTime, relaxationTime and relaxivity set.")

        if self._cwd is None:
            self._cwd = os.path.dirname(AVIDUrlLocater.getExecutableURL(self._session, "MRSignal2ConcentrationMiniApp", actionConfig))


    def _generateName(self):
        name = "signal2concentration_" + self._conversiontype + "_"+ str(artefactHelper.getArtefactProperty(self._signal, artefactProps.ACTIONTAG)) \
               + "_#" + str(artefactHelper.getArtefactProperty(self._signal, artefactProps.TIMEPOINT))
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

        execURL = AVIDUrlLocater.getExecutableURL(self._session, "MRSignal2ConcentrationMiniApp", self._actionConfig)

        content = '"{}" -i "{}" -o "{}" -{}'.format(execURL, signalPath, resultPath, self._conversiontype)
        if self._conversiontype == self.CONVERSION_T1_ABSOLUTE or self._conversiontype == self.CONVERSION_T1_RELATIVE:
            content += ' -k "{}" '.format(self._k)
        elif self._conversiontype == self.CONVERSION_T1_FLASH:
            content += ' -k "{}" --TE "{}"'.format(self._k)
        elif self._conversiontype == self.CONVERSION_T2:
            content += ' --relaxivity "{}" --recovery-time "{}" --relaxation-time "{}"'.format(self._relaxivity, self._recoveryTime, self._relaxationTime)

        return content


class MR2SignalConcentrationMiniAppBatchAction(BatchActionBase):
    '''Batch action for MR2SignalConcentrationMiniApp.'''

    CONVERSION_T1_ABSOLUTE = MR2SignalConcentrationMiniAppAction.CONVERSION_T1_ABSOLUTE
    CONVERSION_T1_RELATIVE = MR2SignalConcentrationMiniAppAction.CONVERSION_T1_RELATIVE
    CONVERSION_T1_FLASH = MR2SignalConcentrationMiniAppAction.CONVERSION_T1_FLASH
    CONVERSION_T2 = MR2SignalConcentrationMiniAppAction.CONVERSION_T2

    def __init__(self, signalSelector,
                 actionTag="MRSignal2Concentration", alwaysDo=False, session=None,
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
