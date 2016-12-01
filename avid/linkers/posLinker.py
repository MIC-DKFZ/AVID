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
  ''' Links only by position. Therefore selection is slaveSelection[masterIndex].
    If masterIndex is larger then len(slaveSelection) it will be the last element
    of the slave selection.
  '''
  def __init__(self):
    pass

  def getLinkedSelection(self,masterIndex, masterSelection, slaveSelection):
    index = masterIndex
    if index > len(slaveSelection):
      index = len(slaveSelection)-1
      
    resultSelection = list(dict(),)

    if index >= 0:
      resultSelection.append(slaveSelection[index])
               
    return resultSelection        
