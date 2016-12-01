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


class CaseInstanceLinker(LinkerBase):
  '''
      Links data on the basis of the artefactProps.CASEINSTANCE entry. 
      If strict linkage is false the linker will also accept instances where
      one of master and slave is none and the other has a defined value.
  '''
  def __init__(self, useStrictLinkage = False):
    '''@param useStrictLinkage If true it will only link with the very same instance id.
      If false, it will treat None as wildcard that also matches.'''
    
    self._useStrictLinkage = useStrictLinkage

    
  def getLinkedSelection(self, masterIndex, masterSelection, slaveSelection):
    
    masterEntry = masterSelection[masterIndex]
    linkValue = None
    if artefactProps.CASEINSTANCE in masterEntry:
      linkValue = masterEntry[artefactProps.CASEINSTANCE]

    resultSelection = list(dict(),)   
    for item in slaveSelection:
      if artefactProps.CASEINSTANCE in item:
        itemValue = item[artefactProps.CASEINSTANCE]
        if itemValue == linkValue\
          or (not self._useStrictLinkage\
              and (linkValue is None or itemValue is None)):
          resultSelection.append(item)
      else:
        if linkValue is None:
          #key does not exist, but selection value is None, therefore it is a match
          resultSelection.append(item)
        
          
    return resultSelection
      