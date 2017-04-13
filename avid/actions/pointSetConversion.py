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
from avid.common import osChecker
import avid.externals.matchPoint as matchpoint
import avid.externals.fcsv as fcsv

from . import BatchActionBase
from . import SingleActionBase
from avid.selectors import TypeSelector
from simpleScheduler import SimpleScheduler
from avid.selectors.keyValueSelector import FormatSelector

logger = logging.getLogger(__name__)


class PointSetConversionAction(SingleActionBase):
  '''Class that convert point sets from one formate to another.'''

  def __init__(self, pointset, targetformat, actionTag="PointSetConversion",
               alwaysDo=True, session=None, additionalActionProps=None, propInheritanceDict = None):
    SingleActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, propInheritanceDict = propInheritanceDict)
    self._pointset = pointset

    self._targetformat = targetformat
    self._addInputArtefacts(pointset=self._pointset)

  def _generateName(self):
    return "Conversion_to_{}".format(self._targetformat)

  def _getExtension(self, format):
    '''returns the extension used for a certain format'''
    if format == matchpoint.FORMAT_VALUE_MATCHPOINT_POINTSET:
      return 'txt'
    elif format == fcsv.FORMAT_VALUE_SLICER_POINTSET:
      return 'fcsv'

  def indicateOutputs(self):

    self._resultArtefact = self.generateArtefact(self._pointset,
                                                 userDefinedProps={artefactProps.TYPE:artefactProps.TYPE_VALUE_RESULT,
                                                                   artefactProps.FORMAT: self._targetformat},
                                                 urlHumanPrefix=self.instanceName,
                                                 urlExtension=self._getExtension(self._targetformat))

    return [self._resultArtefact]

  def _generateOutputs(self):

    sourcePath = artefactHelper.getArtefactProperty(self._pointset, artefactProps.URL)
    sformat = artefactHelper.getArtefactProperty(self._pointset, artefactProps.FORMAT)
    destPath = artefactHelper.getArtefactProperty(self._resultArtefact, artefactProps.URL)

    ps = None

    if sformat is None:
      raise ValueError('Format of source cannot be identified. Source file: {}'.format(sourcePath))
    elif sformat == matchpoint.FORMAT_VALUE_MATCHPOINT_POINTSET:
      ps = matchpoint.read_simple_pointset(sourcePath)
    elif sformat == fcsv.FORMAT_VALUE_SLICER_POINTSET:
      ps = fcsv.read_fcsv(sourcePath)
    else:
      raise ValueError('Format of source is not supported. Unsupported format: {}; source file: {}'.format(sformat, sourcePath))

    if self._targetformat == matchpoint.FORMAT_VALUE_MATCHPOINT_POINTSET:
      matchpoint.write_simple_pointset(destPath,ps)
    elif self._targetformat == fcsv.FORMAT_VALUE_SLICER_POINTSET:
      fcsv.write_fcsv(destPath,ps)
    else:
      raise ValueError(
        'Target format is not supported. Unsupported format: {}; source file: {}'.format(self._targetformat,
                                                                                            sourcePath))

class PointSetConversionBatchAction(BatchActionBase):
  '''Batch class for the point set conversion action.'''

  def __init__(self, pointsetSelector, actionTag="PointSetConversion", alwaysDo=False,
               session=None, additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._inputPSs = pointsetSelector.getSelection(self._session.artefacts)

    self._singleActionParameters = singleActionParameters

  def _generateActions(self):
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)
    pss = self.ensureRelevantArtefacts(self._inputPSs, resultSelector, "point set input")

    actions = list()

    for (pos, ps) in enumerate(pss):
      action = PointSetConversionAction(ps, actionTag = self._actionTag, alwaysDo=self._alwaysDo,
                             session=self._session,
                             additionalActionProps=self._additionalActionProps,
                             **self._singleActionParameters)
      actions.append(action)

    return actions