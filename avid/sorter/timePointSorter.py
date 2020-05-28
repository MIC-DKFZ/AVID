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

from avid.sorter.keyValueSorter import KeyValueSorter

import avid.common.artefact.defaultProps as artefactProps

class TimePointSorter(KeyValueSorter):
  '''Special version that enforces that time point is sorted as numeric.'''
  def __init__(self, reverse = False):
    KeyValueSorter.__init__(key=artefactProps.TIMEPOINT, reverse= reverse, asNumbers=True)
