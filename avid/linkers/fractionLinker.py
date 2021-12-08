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

from avid.linkers import InnerLinkerBase
from .keyValueLinker import CaseLinker
from .caseInstanceLinker import CaseInstanceLinker
from .keyValueLinker import TimePointLinker
import avid.common.artefact as artefactHelper
import avid.common.artefact.defaultProps as artefactProps

class FractionLinker(InnerLinkerBase):
  '''
      Links fraction data. This implies that the entries have the same case, case instance and timepoint
      Allows to also link to the nearest time point in the past, if
      current time point is not available.
  '''
  def __init__(self, useClosestPast = False, allowOnlyFullLinkage=True, performInternalLinkage=False):
    '''@param useClosestPast If true it will check also for the largest timepoint
    smaller then the actual timepoint and links against it.
    '''
    InnerLinkerBase.__init__(self, allowOnlyFullLinkage=allowOnlyFullLinkage,
                             performInternalLinkage=performInternalLinkage)
    self._useClosestPast = useClosestPast
    self._caseLinker = CaseLinker(allowOnlyFullLinkage=allowOnlyFullLinkage,
                                  performInternalLinkage=performInternalLinkage)
    self._caseInstanceLinker = CaseInstanceLinker(allowOnlyFullLinkage=allowOnlyFullLinkage,
                                  performInternalLinkage=performInternalLinkage)
    self._timePointLinker = TimePointLinker(allowOnlyFullLinkage=allowOnlyFullLinkage,
                                  performInternalLinkage=performInternalLinkage)

  def _findLinkedArtefactOptions(self, primaryArtefact, secondarySelection):

    preFilteredResult = self._caseLinker._findLinkedArtefactOptions(primaryArtefact=primaryArtefact,
                                                         secondarySelection=secondarySelection)
    preFilteredResult = self._caseInstanceLinker._findLinkedArtefactOptions(primaryArtefact=primaryArtefact,
                                                         secondarySelection=preFilteredResult)
    result = list()

    if self._useClosestPast:
      masterTimePoint = float(artefactHelper.getArtefactProperty(primaryArtefact, artefactProps.TIMEPOINT))
      bestArtefact = None
      bestTimePoint = float('-inf')
      # search for the best time fit
      for secondaryArtefact in preFilteredResult:
        try:
          timePoint = float(artefactHelper.getArtefactProperty(secondaryArtefact, artefactProps.TIMEPOINT))
          if bestTimePoint < timePoint <= masterTimePoint:
            bestTimePoint = timePoint
            bestArtefact = secondaryArtefact
        except:
          pass

      if bestArtefact is not None:
        result.append(bestArtefact)
    else:
      result = self._timePointLinker._findLinkedArtefactOptions(primaryArtefact=primaryArtefact,
                                                                secondarySelection=preFilteredResult)
    return result

  def _getLinkedSelection(self, primaryIndex, primarySelections, secondarySelections):
    '''Filters the given primary selections and returns the selection that is as
    close as possible in time to the primary selection.
    In the current implementation it is simplfied by just checking the timepoint of the first artefact of each
    selection.'''

    #the following call finds all secondary collections that qualify as potantial fit.
    #this is done by implicitly calling FractionLinker._findLinkedArtefactOptions
    preFilterdResult = InnerLinkerBase._getLinkedSelection(self,primaryIndex=primaryIndex, primarySelections=primarySelections,
                                                 secondarySelections=secondarySelections)
    primarySelection = primarySelections[primaryIndex]
    preFilterdResult = self._sanityCheck(primarySelection=primarySelection, linkedSelections=preFilterdResult)

    result = list()

    #now we have to find the secondary selection that is closest to the primary selection as FractionLinker always
    #returns the closest option.
    try:
      masterTimePoint = float(artefactHelper.getArtefactProperty(primarySelection[0], artefactProps.TIMEPOINT))
      bestTimePoint = float('-inf')
      for selection in preFilterdResult:
        try:
          if selection[0] is None:
            timePoint = float('-inf')
          else:
            timePoint = float(artefactHelper.getArtefactProperty(selection[0], artefactProps.TIMEPOINT))

          if bestTimePoint <= timePoint <= masterTimePoint:
            if timePoint > bestTimePoint:
              result.clear()
            bestTimePoint = timePoint
            result.append(selection)
        except:
          pass
    except:
      pass

    return result
