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

import logging

import avid.common.artefact.defaultProps as artefactProps
from avid.selectors import TypeSelector
from . import BatchActionBase
from .genericCLIAction import GenericCLIAction
from .simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)


class MitkMRSignal2ConcentrationMiniAppAction(GenericCLIAction):
    """Class that wrapps the single action for the tool MitkMRSignal2ConcentrationMiniApp."""
    CONVERSION_T1_ABSOLUTE = "t1-absolute"
    CONVERSION_T1_RELATIVE = "t1-relative"
    CONVERSION_T1_FLASH = "t1-flash"
    CONVERSION_T2 = "t2"

    def __init__(self, signal, conversiontype=CONVERSION_T1_ABSOLUTE, k=1, recoveryTime=None,
                 relaxivity=None, relaxationTime=None, te=None, actionTag="MitkMRSignal2Concentration", alwaysDo=False,
                 session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None):

        signal = self._ensureSingleArtefact(signal, "signal")

        self._conversiontype = conversiontype
        self._k = k
        self._recoveryTime = recoveryTime
        self._relaxivity = relaxivity
        self._relaxationTime = relaxationTime
        self._te = te

        if te is None and conversiontype == self.CONVERSION_T2:
            raise RuntimeError("Cannot convert T2 without parameter TE set.")
        if conversiontype == self.CONVERSION_T1_FLASH and (
                recoveryTime is None or relaxationTime is None or relaxivity is None):
            raise RuntimeError(
                "Cannot convert T1 flash without parameter recoveryTime, relaxationTime and relaxivity set.")

        additionalArgs = {self._conversiontype: None}
        if self._conversiontype == self.CONVERSION_T1_ABSOLUTE or self._conversiontype == self.CONVERSION_T1_RELATIVE:
            additionalArgs['k'] = self._k
        elif self._conversiontype == self.CONVERSION_T1_FLASH:
            additionalArgs['k'] = self._k
            additionalArgs['TE'] = self._te
        elif self._conversiontype == self.CONVERSION_T2:
            additionalArgs['relaxivity'] = self._relaxivity
            additionalArgs['recovery-time'] = self._recoveryTime
            additionalArgs['relaxation-time'] = self._relaxationTime

        if additionalActionProps is None:
            additionalActionProps = dict()
        additionalActionProps[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_ITK

        GenericCLIAction.__init__(self, i=[signal], actionID="MitkMRSignal2ConcentrationMiniApp",
                                  outputFlags=['o'],
                                  additionalArgs=additionalArgs,
                                  actionTag=actionTag, alwaysDo=alwaysDo, session=session,
                                  additionalActionProps=additionalActionProps, actionConfig=actionConfig,
                                  propInheritanceDict=propInheritanceDict,
                                  defaultoutputextension='nrrd')


class MitkMRSignal2ConcentrationMiniAppBatchAction(BatchActionBase):
    """Batch action for MitkMRSignal2ConcentrationMiniApp."""

    CONVERSION_T1_ABSOLUTE = MitkMRSignal2ConcentrationMiniAppAction.CONVERSION_T1_ABSOLUTE
    CONVERSION_T1_RELATIVE = MitkMRSignal2ConcentrationMiniAppAction.CONVERSION_T1_RELATIVE
    CONVERSION_T1_FLASH = MitkMRSignal2ConcentrationMiniAppAction.CONVERSION_T1_FLASH
    CONVERSION_T2 = MitkMRSignal2ConcentrationMiniAppAction.CONVERSION_T2

    def __init__(self, signalSelector, actionTag='MitkMRSignal2Concentration', session=None,
                 additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
        BatchActionBase.__init__(self, actionTag=actionTag, actionClass=MitkMRSignal2ConcentrationMiniAppAction,
                                 primaryInputSelector=signalSelector,
                                 primaryAlias="signal", session=session,
                                 relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps=additionalActionProps,
                                 **singleActionParameters)
