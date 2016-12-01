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

class LinkerBase(object):
  ''' Linkers serve as delegate to generate sub selection that have some semantic
      linkage to the masterEntry (e.g. have the same case id or time point)
  '''
  def __init__(self):
    pass
      
  def getLinkedSelection(self, masterIndex, masterSelection, slaveSelection):
    ''' Get the sub selection of slave that has a meaningful semantic link
        to the master selection/index. The default implementation just passes through
        the slaveSelection (so everything gets linked).
        @result List of all linked artefacts. Therefore all artefacts from slave selection
        that fullfill the link criterion in respect to the master artefact.
        @param masterIndex index of the entry in the masterSelection that is defining
        for the link.
        @param masterSelection the master selection that contains the master entry
        @param slaveSelection that is used to generate the subset. '''
    return slaveSelection

  def __add__(self,other):
    ''' Creates an AndLinker with both operands.'''
    andLinker = AndLinker(self,other)
    return andLinker


class AndLinker(LinkerBase):
  '''
      Special linker that works like an and operation on to child linkers.
      The selection result of the AndLinker is the intersection of the selection
      of both child linkers.
  '''
  def __init__(self, linker1, linker2):
    ''' init '''
    self._linker1 = linker1
    self._linker2 = linker2

  def getLinkedSelection(self,masterIndex, masterSelection, slaveSelection):
    '''Filters the given list of entries and returns all selected entries'''
    selection1 = self._linker1.getLinkedSelection(masterIndex, masterSelection, slaveSelection)
    selection2 = self._linker2.getLinkedSelection(masterIndex, masterSelection, slaveSelection)
    resultSelection = list(dict(),)
    for item1 in selection1:
      for item2 in selection2:
        if item1 == item2:
          resultSelection.append(item1)
          selection2.remove(item2)
          break
          
    return resultSelection


from keyValueLinker import KeyValueLinker
from keyValueLinker import CaseLinker
from keyValueLinker import TimePointLinker
from fractionLinker import FractionLinker
from caseInstanceLinker import CaseInstanceLinker