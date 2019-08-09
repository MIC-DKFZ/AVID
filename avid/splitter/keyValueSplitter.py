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

class KeyValueSplitter(BaseSplitter):
  '''Splits the artefacts in such a way that all artefacts in a splitt list have the same values for all specified keys
  respectively. So it is a simelar behavour than function splitArtefact().'''
  def __init__(self, *splitArgs):
    '''@param splitArgs the function assumes that all unkown arguments passed to the function should be handeled as split
     properties keys that are used to specify the split.'''
    self._key = splitArgs

  def splitSelection(self, selection):
    return splitArtefact(inputArtefacts = selection, *self._key)