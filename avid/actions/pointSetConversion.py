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

import avid.common.artefact as artefactHelper
import avid.common.artefact.defaultProps as artefactProps
import avid.externals.fcsv as fcsv
import avid.externals.matchPoint as matchpoint
from avid.selectors import TypeSelector
from . import BatchActionBase
from . import SingleActionBase
from .simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)


class PointSetConversionAction(SingleActionBase):
    """Class that convert point sets from one formate to another."""

    def __init__(self, pointset, targetformat, actionTag="PointSetConversion",
                 alwaysDo=True, session=None, additionalActionProps=None, propInheritanceDict=None):
        SingleActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps,
                                  propInheritanceDict=propInheritanceDict)
        self._addInputArtefacts(pointset=pointset)
        self._pointset = self._ensureSingleArtefact(pointset, 'pointset')
        self._targetformat = targetformat

    def _generateName(self):
        return "Conversion_{}_to_{}".format(artefactHelper.getArtefactShortName(self._pointset), self._targetformat)

    @staticmethod
    def _getExtension(format_value):
        """returns the extension used for a certain format"""
        if format_value == matchpoint.FORMAT_VALUE_MATCHPOINT_POINTSET:
            return 'txt'
        elif format_value == fcsv.FORMAT_VALUE_SLICER_POINTSET:
            return 'fcsv'

    def _indicateOutputs(self):

        resultArtefact = self.generateArtefact(self._pointset,
                                               userDefinedProps={artefactProps.TYPE: artefactProps.TYPE_VALUE_RESULT,
                                                                 artefactProps.FORMAT: self._targetformat},
                                               urlHumanPrefix=self.instanceName,
                                               urlExtension=self._getExtension(self._targetformat))
        return [resultArtefact]

    def _generateOutputs(self):
        sourcePath = artefactHelper.getArtefactProperty(self._pointset, artefactProps.URL)
        sformat = artefactHelper.getArtefactProperty(self._pointset, artefactProps.FORMAT)
        destPath = artefactHelper.getArtefactProperty(self.outputArtefacts[0], artefactProps.URL)

        ps = None

        if sformat is None:
            raise ValueError('Format of source cannot be identified. Source file: {}'.format(sourcePath))
        elif sformat == matchpoint.FORMAT_VALUE_MATCHPOINT_POINTSET:
            ps = matchpoint.read_simple_pointset(sourcePath)
        elif sformat == fcsv.FORMAT_VALUE_SLICER_POINTSET:
            ps = fcsv.read_fcsv(sourcePath)
        else:
            raise ValueError(
                'Format of source is not supported. Unsupported format: {}; source file: {}'.format(sformat,
                                                                                                    sourcePath))

        if self._targetformat == matchpoint.FORMAT_VALUE_MATCHPOINT_POINTSET:
            matchpoint.write_simple_pointset(destPath, ps)
        elif self._targetformat == fcsv.FORMAT_VALUE_SLICER_POINTSET:
            fcsv.write_fcsv(destPath, ps)
        else:
            raise ValueError(
                'Target format is not supported. Unsupported format: {}; source file: {}'.format(self._targetformat,
                                                                                                 sourcePath))


class PointSetConversionBatchAction(BatchActionBase):
    """Batch class for the point set conversion action."""

    def __init__(self, pointsetSelector, actionTag="PointSetConversion", session=None, additionalActionProps=None,
                 scheduler=SimpleScheduler(), **singleActionParameters):
        BatchActionBase.__init__(self, actionTag=actionTag, actionClass=PointSetConversionAction,
                                 primaryInputSelector=pointsetSelector, primaryAlias="pointset",
                                 session=session, relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler,
                                 additionalActionProps=additionalActionProps, **singleActionParameters)
