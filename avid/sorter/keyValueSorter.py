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

from avid.sorter import BaseSorter

class KeyValueSorter(BaseSorter):
  '''Sorts the selection by the values of a passed property key.'''
  def __init__(self, key, reverse=False, asNumbers=False):
    '''@param asNumbers: If true the sort values will be converted to numbers before sorting and not sorted as strings.'''
    super().__init__()
    self._key = key
    self._reverse = reverse
    self._asNumbers = asNumbers
        
  def sortSelection(self, selection):
    sortedSel = None
    if self._asNumbers:
      sortedSel= sorted(selection, key=lambda k: float(k[self._key]), reverse = self._reverse)
    else:
      sortedSel = sorted(selection, key=lambda k: k[self._key], reverse=self._reverse)
    return sortedSel