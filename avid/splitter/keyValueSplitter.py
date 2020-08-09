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

from avid.splitter import BaseSplitter
from avid.common.demultiplexer import splitArtefact
import avid.common.artefact.defaultProps as artefactProps

class KeyValueSplitter(BaseSplitter):
  '''Splits the artefacts in such a way that all artefacts in a splitt list have the same values for all specified keys
  respectively. So it is a simelar behavour than function splitArtefact().'''
  def __init__(self, *splitArgs):
    '''@param splitArgs the function assumes that all unkown arguments passed to the function should be handeled as split
     properties keys that are used to specify the split.'''
    self._key = splitArgs

  def splitSelection(self, selection):
    return splitArtefact(selection, *self._key)

class CaseSplitter(KeyValueSplitter):
  '''Splits artefact in such a way that all artefacts of same case are in one split.'''
  def __init__(self):
    KeyValueSplitter.__init__(self, artefactProps.CASE)

class FractionSplitter(KeyValueSplitter):
  '''Splits artefact in such a way that all artefacts of same case and timepoint are in one split.'''
  def __init__(self):
    KeyValueSplitter.__init__(self, artefactProps.CASE, artefactProps.TIMEPOINT)
