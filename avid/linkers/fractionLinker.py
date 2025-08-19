# SPDX-FileCopyrightText: 2024, German Cancer Research Center (DKFZ), Division of Medical Image Computing (MIC)
#
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# or find it in LICENSE.txt.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
    masterTimePoint = float(artefactHelper.getArtefactProperty(next(iter(primarySelection)), artefactProps.TIMEPOINT))
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

    return result
