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

from avid.linkers import LinkerBase

import avid.common.artefact.defaultProps as artefactProps

class KeyValueLinker(LinkerBase):
  '''
      Links data based on the value of a given key.
  '''
  def __init__(self, key, checkAllPrimaryArtefacts = True):
    '''@param checkAllPrimaryArtefacts indicates if all artefacts of the primary selection must find at least one
      matching artefact in the secondary selection to count as semantically linked. If false, it is enough that
      on primary artefact finds a match.'''
    self.__key = key
    self.__checkAllPrimaryArtefacts = checkAllPrimaryArtefacts
      
  def getLinkedSelection(self, primaryIndex, primarySelections, secondarySelections):
    '''Filters the given list of entries and returns all selected entries'''
    primarySelection = primarySelections[primaryIndex]

    resultSelections = list(list(),)
    for secondSelection in secondarySelections:

      addSelection = False
      if self.__checkAllPrimaryArtefacts:
        addSelection = True;

      for primeArtefact in primarySelection:
        linkValue = None
        if self.__key in primeArtefact:
          linkValue = primeArtefact[self.__key]
        hasLink = False

        for secondArtefact in secondSelection:
          if self.__key in secondArtefact:
            if secondArtefact[self.__key] == linkValue:
              hasLink = True
              break
          else:
            if linkValue is None:
              #key does not exist, but selection value is None, therefore it is a match
              hasLink = True
              break

        if hasLink and not self.__checkAllPrimaryArtefacts:
          addSelection = True
          break
        elif not hasLink and self.__checkAllPrimaryArtefacts:
          addSelection = False
          break

      if addSelection:
        resultSelections.append(secondSelection)
          
    return resultSelections
  
    
class CaseLinker(KeyValueLinker):
  '''
      Links data on the basis of the artefactProps.CASE entry 
      usually the patient information is stored in case.
  '''
  def __init__(self):
    KeyValueLinker.__init__(self, artefactProps.CASE)

    

class TimePointLinker(KeyValueLinker):
  '''
      Links data on the basis of the artefactProps.TIMEPOINT entry 
      usually the patient information is stored in case.
  '''
  def __init__(self):
    KeyValueLinker.__init__(self, artefactProps.TIMEPOINT)