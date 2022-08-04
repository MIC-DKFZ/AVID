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
import os
from shutil import copyfile

import avid.common.artefact as artefactHelper
import avid.common.artefact.defaultProps as artefactProps
from avid.externals.matchPoint import FORMAT_VALUE_MATCHPOINT, getDeformationFieldPath
from avid.externals.plastimatch import FORMAT_VALUE_PLM_CXT
from avid.linkers import CaseLinker
from avid.selectors import TypeSelector
from . import BatchActionBase
from .genericCLIAction import GenericCLIAction, extract_artefact_arg_urls_default
from .simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)


class PlmRTSSMapAction(GenericCLIAction):
    """Class that wraps the single action for the tool plastimatch convert in order to map DICOM RT SS via a
    registration. """

    @staticmethod
    def _plmRTSS_url_extraction_delegate(arg_name, arg_value):
        result = list()
        if arg_name == 'xf':
            for arg_artefact in arg_value:
                regPath = artefactHelper.getArtefactProperty(arg_artefact, artefactProps.URL)
                regFormat = artefactHelper.getArtefactProperty(arg_artefact, artefactProps.FORMAT)
                if regFormat == FORMAT_VALUE_MATCHPOINT:
                    fieldPath = getDeformationFieldPath(regPath)
                    if fieldPath is None:
                        raise RuntimeError(
                            "Cannot extract deformation field path from the given registration. Reg File: {}".format(
                                regPath))
                    else:
                        regPath = fieldPath
                result.append(regPath)
        else:
            result = extract_artefact_arg_urls_default(arg_name=arg_name, arg_value=arg_value)

        return result

    def __init__(self, rtss, registration, outputFormat=artefactProps.FORMAT_VALUE_DCM,
                 actionTag="plmRTSSMap", alwaysDo=False,
                 session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None, cli_connector=None):

        rtss = self._ensureSingleArtefact(rtss, "rtss")
        registration = self._ensureSingleArtefact(registration, "registration")
        self._outputFormat = outputFormat

        inputArgs = {'input': [rtss]}
        if registration is not None:
            inputArgs['xf'] = [registration]

        GenericCLIAction.__init__(self, **inputArgs, actionID="plastimatch",
                                  noOutputArgs=True,
                                  argPositions=['command'],
                                  additionalArgsAsURL=['output-dicom', 'output-cxt'],
                                  inputArgsURLExtractionDelegate=self._plmRTSS_url_extraction_delegate,
                                  actionTag=actionTag, alwaysDo=alwaysDo, session=session,
                                  additionalActionProps=additionalActionProps, actionConfig=actionConfig,
                                  propInheritanceDict=propInheritanceDict, cli_connector=cli_connector,
                                  defaultoutputextension=self._getOutputExtension())

        additionalArgs = {'command': 'convert'}
        resultPath = artefactHelper.getArtefactProperty(self.outputArtefacts[0], artefactProps.URL)
        if self._outputFormat == artefactProps.FORMAT_VALUE_DCM:
            additionalArgs['output-dicom'] = os.path.splitext(resultPath)[0]
        elif self._outputFormat == FORMAT_VALUE_PLM_CXT:
            additionalArgs['output-cxt'] = resultPath
        else:
            raise ValueError(
                'Output format is not supported by plmRTSSMap action. Choosen format: {}'.format(self._outputFormat))

        self.setAdditionalArguments(additionalArgs=additionalArgs)

    def _getOutputExtension(self):
        if self._outputFormat == artefactProps.FORMAT_VALUE_DCM:
            return 'dcm'
        elif self._outputFormat == FORMAT_VALUE_PLM_CXT:
            return 'cxt'
        else:
            raise ValueError(
                'Output format is not supported by plmRTSSMap action. Choosen format: {}'.format(self._outputFormat))

    def _postProcessCLIExecution(self):
        if self._outputFormat == artefactProps.FORMAT_VALUE_DCM:
            resultPath = artefactHelper.getArtefactProperty(self.outputArtefacts[0], artefactProps.URL)
            dicomDir = os.path.splitext(resultPath)[0]

            for file in os.listdir(dicomDir):
                copyfile(os.path.join(dicomDir, file), resultPath)
                break  # we assume that plastimatch outputs only on file (the warpped/mapped RT structure set) in the
                # result dir


class PlmRTSSMapBatchAction(BatchActionBase):
    """Batch action for PlmRTSSMapAction."""

    def __init__(self, rtssSelector, regSelector=None, regLinker=None, actionTag="plmRTSSMap", session=None,
                 additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
        if regLinker is None:
            regLinker = CaseLinker()

        additionalInputSelectors = {"registration": regSelector}
        linker = {"registration": regLinker}

        BatchActionBase.__init__(self, actionTag=actionTag, actionClass=PlmRTSSMapAction,
                                 primaryInputSelector=rtssSelector,
                                 primaryAlias="rtss", additionalInputSelectors=additionalInputSelectors,
                                 linker=linker, session=session,
                                 relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps=additionalActionProps,
                                 **singleActionParameters)
