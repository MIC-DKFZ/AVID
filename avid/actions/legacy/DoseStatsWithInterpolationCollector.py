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

from builtins import str
from builtins import range
import os
import logging
import csv

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper
from avid.common import osChecker
import avid.externals.doseTool as doseTool

from avid.actions import BatchActionBase
from avid.actions import SingleActionBase
from avid.selectors import TypeSelector
from avid.actions.simpleScheduler import SimpleScheduler
from avid.selectors.keyValueSelector import FormatSelector

logger = logging.getLogger(__name__)

class DoseStatsWithInterpolationCollectorAction(SingleActionBase):
  '''Class that establishes a dose stats collection action for one timepoint. The in-between values will be interpolated. The result will be stored as CSV'''

  def __init__(self, doseSelection, planSelection, selectedStats = None, rowKey = artefactProps.CASEINSTANCE,
               columnKey = artefactProps.TIMEPOINT,
               withHeaders = True, actionTag = "DoseStatWithInterpolationCollector",
               alwaysDo = False, session = None, additionalActionProps = None):
    SingleActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps)
    self._doseSelection = doseSelection
    self._planSelection = planSelection

    self._statsMatrix = None
    self._keys = selectedStats
    self._rowKey = rowKey
    self._columnKey = columnKey
    self._rowValues = sorted(set([d[rowKey] for d in doseSelection]))
    self._columnValues = sorted(set([d[columnKey] for d in doseSelection]))
    self._resultArtefacts = dict()
    self._withHeaders = withHeaders

  def _generateName(self):
    name = "stat_collection_interpolation_"+self._rowKey+"_x_"+self._columnKey

    return name

  def _indicateOutputs(self):
    self._statsMatrix = self._generateStatsMatrix()
    if self._keys is None:
      self._keys = list(self._statsMatrix.keys())

    name = self.instanceName

    for key in self._keys:
      if len(self._doseSelection)>0:
        artefact = self.generateArtefact(self._doseSelections[0],
                                                     userDefinedProps={
                                                       artefactProps.TYPE: artefactProps.TYPE_VALUE_RESULT,
                                                       artefactProps.FORMAT: artefactProps.FORMAT_VALUE_CSV,
                                                       artefactProps.DOSE_STAT: str(key)},
                                                     urlHumanPrefix=self.instanceName,
                                                     urlExtension='csv')
        self._resultArtefacts[key] = artefact

    return list(self._resultArtefacts.values())


  def _parseDoseStats(self, filename, statsOfInterest):
    """get relevant values from file (DoseStatistics)"""
    resultContainer = doseTool.loadResult(filename)

    doseMapOneFraction = {}
    if statsOfInterest is None:
      statsOfInterest = list(resultContainer.results.keys()) #if user hasn't defined something we take all

    for key in statsOfInterest:
      if key in resultContainer.results:
        doseMapOneFraction[key] = resultContainer.results[key].value
      else:
        logger.warning("Stat key '%s' selected by user, was not found in parsed statistic file. File: %s", key, filename)

    return doseMapOneFraction


  def _generateStatsMatrix(self):
    '''generates and returns a n-dimensional value matrix.
    1st dim is indexed by the dose state key values
    2nd dim is indexed by the rowKey values
    3rd dim is indexed by the columnKey values'''
    matrix = dict()

    keys = self._keys

    for artefact in self._doseSelection:
      aPath = artefactHelper.getArtefactProperty(artefact,artefactProps.URL)
      rowID = 0 #there is only one row
      columnID = artefactHelper.getArtefactProperty(artefact,self._columnKey)
      valueMap = self._parseDoseStats(aPath, self._keys)

      if keys is None:
        keys = list(valueMap.keys()) #user has not select keys -> take everything

      for key in keys:
        if key in valueMap:
          if key not in matrix:
            matrix[key] = dict()

          if rowID not in matrix[key]:
            matrix[key][rowID] = dict()

          matrix[key][rowID][columnID] = valueMap[key]

    return matrix


  def _generateRow(self, rowValue, nPlannedFractions):
    '''ensures that a row covers a certain key range. missing keys will be filled with None.
       the row will be returned as list of values'''
    result = list()

    for fraction in range(1,nPlannedFractions+1):
      result.append(rowValue*float(fraction)/float(nPlannedFractions))

    return result


  def _writeToCSV(self, key, columnHeaders, content, filename):
    try:
      osChecker.checkAndCreateDir(os.path.split(filename)[0])
      with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')

        if self._withHeaders:
          writer.writerow([self._rowKey+"/" +self._columnKey] + columnHeaders)

        '''write given values'''
        for rowID in sorted(content):
          row = content[rowID]
          if self._withHeaders:
            row = [str(rowID)] + row
          writer.writerow(row)

    except:
      print("CSV file writing error. Aborting...")
      raise


  def _generateOutputs(self):
    nPlannedFractions = int(artefactHelper.getArtefactProperty(self._planSelection[0],"planned_fractions"))
    for key in self._keys:
      csvPath = artefactHelper.getArtefactProperty(self._resultArtefacts[key],artefactProps.URL)
      keyMatrix = self._statsMatrix[key]
      columnHeaderValues = list(range(1,nPlannedFractions+1))
      csvContent = dict()
      for rowID in sorted(keyMatrix):
        if len(keyMatrix[rowID]) == 1:
          value = float(keyMatrix[rowID][0])
          row = self._generateRow(value, nPlannedFractions)
          csvContent[rowID] = row
        else:
          logger.warning("planned DoseStats contains != 1 entry.")

      self._writeToCSV(key, columnHeaderValues, csvContent, csvPath)


class DoseStatsWithInterpolationCollectorBatchAction(BatchActionBase):
  '''Batch class for the dose collection actions.'''

  def __init__(self,  inputSelector, planSelector, selectedStats = None, rowKey = artefactProps.CASEINSTANCE,
               columnKey = artefactProps.TIMEPOINT, withHeaders = True,
               actionTag = "doseStatWithInterpolationCollector", alwaysDo = False,
               session = None, additionalActionProps = None, scheduler = SimpleScheduler()):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._inputStats = inputSelector.getSelection(self._session.artefacts)
    self._plan = planSelector.getSelection(self._session.artefacts)

    self._rowKey = rowKey
    self._columnKey = columnKey
    self._selectedStats = selectedStats
    self._withHeaders = withHeaders


  def _generateActions(self):
    #filter only type result. Other artefact types are not interesting
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT) + FormatSelector(artefactProps.FORMAT_VALUE_RTTB_STATS_XML)
    planSelector =  TypeSelector(artefactProps.TYPE_VALUE_RESULT)

    inputs = self.ensureRelevantArtefacts(self._inputStats, resultSelector, "input stats")
    plan = self.ensureRelevantArtefacts(self._plan, planSelector, "plan")

    global logger
    if len(inputs) == 0 or len (plan) == 0 :
      logger.debug("Input selection contains no usable artefacts (type = result).")
    actions = list()

    action = DoseStatsWithInterpolationCollectorAction(inputs, plan, self._selectedStats, self._rowKey,
               self._columnKey, self._withHeaders, self._actionTag,
               self._alwaysDo, self._session, self._additionalActionProps)
    actions.append(action)

    return actions