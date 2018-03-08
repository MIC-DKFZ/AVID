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
from .keyValueLinker import CaseLinker
from .caseInstanceLinker import CaseInstanceLinker
from .keyValueLinker import TimePointLinker
import avid.common.artefact as artefactHelper
import avid.common.artefact.defaultProps as artefactProps

class FractionLinker(LinkerBase):
  '''
      Links fraction data. This implies that the entries have the same case, case instance and timepoint
      Allows to also link to the nearest time point in the past, if
      current time point is not available.
  '''
  def __init__(self, useClosestPast = False):
    '''@param useClosestPast If true it will check also for the largest timepoint
    smaller then the actual timepoint and links against it.'''
    
    self._useClosestPast = useClosestPast

    
  def getLinkedSelection(self, masterIndex, masterSelection, slaveSelection):
    
    linker = CaseLinker() + CaseInstanceLinker()
    
    if not self._useClosestPast:
      linker = linker + TimePointLinker()

    resultSelection = linker.getLinkedSelection(masterIndex,masterSelection, slaveSelection)
    
    if self._useClosestPast and len(resultSelection)>0:
      masterTimePoint = float(artefactHelper.getArtefactProperty(masterSelection[masterIndex],artefactProps.TIMEPOINT))
      bestSelection = None
      bestTimePoint = -1
      #search for the best time fit
      for aLink in resultSelection:
        try:
          timePoint = float(artefactHelper.getArtefactProperty(aLink,artefactProps.TIMEPOINT))
          if timePoint > bestTimePoint and timePoint <= masterTimePoint:
            bestTimePoint = timePoint
            bestSelection = aLink
        except:
          pass
        
      resultSelection = [bestSelection]
         
    return resultSelection
  