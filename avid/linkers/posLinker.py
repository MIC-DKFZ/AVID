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

from .__init__ import LinkerBase

class PosLinker(LinkerBase):
  ''' Links only by position. Therefore selection is secondarySelection[primaryIndex].
    If primaryIndex is larger then len(secondarySelection) it will be the last element
    of the slave selection.
  '''
  def __init__(self):
    LinkerBase.__init__(self, allowOnlyFullLinkage=False)

  def _getLinkedSelection(self, primaryIndex, primarySelections, secondarySelections):
    index = primaryIndex
    if index > len(secondarySelections):
      index = len(secondarySelections) - 1
      
    resultSelections = list(list(),)

    if index >= 0:
      resultSelections.append(secondarySelections[index])
               
    return resultSelections
