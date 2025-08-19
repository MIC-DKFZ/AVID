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
from avid.splitter import BaseSplitter

logger = logging.getLogger(__name__)


def _getColumnHeaderValues(matrix):
    headers = list()

    for key in matrix:
        rowMatrix = matrix[key]
        columnKeys = list(rowMatrix.keys())
        headers.extend(columnKeys)

    # ensure everything is unique and sorted
    uniqueHeaders = set(headers)
    return sorted(uniqueHeaders)


class DoseStatsCollectorAction(SingleActionBase):
    """Class that establishes a dose stats collection action on result generate by DoseTool.
       The result will be stored as CSV"""
    def __init__(self, doses, selectedStats=None, rowKey=artefactProps.CASEINSTANCE,
                 columnKey=artefactProps.TIMEPOINT,
                 withHeaders=True, actionTag="DoseStatCollector",
                 alwaysDo=True, session=None, additionalActionProps=None, propInheritanceDict=None):
        SingleActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps,
                                  propInheritanceDict=propInheritanceDict)
        self._doseSelections = self._ensureArtefacts(doses, 'doses')

        self._statsMatrix = None
        self._baseLineValues = None
        self._keys = selectedStats
        self._rowKey = rowKey
        self._columnKey = columnKey
        self._resultArtefacts = dict()
        self._withHeaders = withHeaders
        self._addInputArtefacts(doses=self._doseSelections)

    def _generateName(self):
        name = "stat_collection_" + self._rowKey + "_x_" + self._columnKey
        return name

    def _indicateOutputs(self):
        if self._keys is None:
            self._statsMatrix = self._generateStatsMatrix()
            self._keys = list(self._statsMatrix.keys())

        for key in self._keys:
            if len(self._doseSelections) > 0:
                artefact = self.generateArtefact(self._doseSelections.first(),
                                                 userDefinedProps={
                                                     artefactProps.TYPE: artefactProps.TYPE_VALUE_RESULT,
                                                     artefactProps.FORMAT: artefactProps.FORMAT_VALUE_CSV,
                                                     artefactProps.DOSE_STAT: str(key)},
                                                 url_user_defined_part=self.instanceName + "_" + str(key),
                                                 url_extension='csv')
                self._resultArtefacts[key] = artefact

        return list(self._resultArtefacts.values())

    @staticmethod
    def _parseDoseStats(filename, statsOfInterest):
        """get relevant values from file (DoseStatistics)"""
        resultContainer = doseTool.loadResult(filename)

        doseMapOneFraction = {}
        if statsOfInterest is None:
            statsOfInterest = list(resultContainer.results.keys())  # if user hasn't defined something we take all

        for key in statsOfInterest:
            if key in resultContainer.results:
                doseMapOneFraction[key] = resultContainer.results[key].value
            else:
                logger.warning("Stat key '%s' selected by user, was not found in parsed statistic file. File: %s", key,
                               filename)

        return doseMapOneFraction

    def _generateStatsMatrix(self):
        """generates and returns a n-dimensional value matrix.
    1st dim is indexed by the dose state key values
    2nd dim is indexed by the rowKey values
    3rd dim is indexed by the columnKey values"""
        matrix = dict()

        keys = self._keys

        for artefact in self._doseSelections:
            aPath = artefactHelper.getArtefactProperty(artefact, artefactProps.URL)
            rowID = artefactHelper.getArtefactProperty(artefact, self._rowKey)
            columnID = artefactHelper.getArtefactProperty(artefact, self._columnKey)
            valueMap = dict()

            if not artefact.is_invalid():
                valueMap = self._parseDoseStats(aPath, self._keys)

            if keys is None:
                keys = list(valueMap.keys())  # user has not select keys -> take everything

            for key in keys:
                if key in valueMap:
                    if key not in matrix:
                        matrix[key] = dict()

                    if rowID not in matrix[key]:
                        matrix[key][rowID] = dict()

                    matrix[key][rowID][columnID] = valueMap[key]

        return matrix

    @staticmethod
    def _generateRow(rowValueDict, columnHeaderValues):
        """ensures that a row covers a certain key range. missing keys will be filled with None.
       the row will be returned as list of values"""
        result = list()

        for key in columnHeaderValues:
            if key in rowValueDict:
                result.append(rowValueDict[key])
            else:
                result.append(None)

        # @TODO Interpolation of missing values. Is this feature still needed?

        return result

    def _writeToCSV(self, key, columnHeaders, content, filename):
        try:
            osChecker.checkAndCreateDir(os.path.split(filename)[0])
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')

                if self._withHeaders:
                    writer.writerow([self._rowKey + "/" + self._columnKey] + columnHeaders)

                '''write given values'''
                for rowID in sorted(content):
                    row = content[rowID]
                    if self._withHeaders:
                        row = [str(rowID)] + row
                    writer.writerow(row)
        except Exception as exc:
            logger.error("CSV file writing error. Reason: {0}".format(exc))
            raise

    def _generateOutputs(self):
        if self._statsMatrix is None:
            self._statsMatrix = self._generateStatsMatrix()

        for key in self._keys:
            csvPath = artefactHelper.getArtefactProperty(self._resultArtefacts[key], artefactProps.URL)
            keyMatrix = self._statsMatrix[key]
            columnHeaderValues = _getColumnHeaderValues(keyMatrix)
            csvContent = dict()
            for rowID in sorted(keyMatrix):
                values = keyMatrix[rowID]
                row = self._generateRow(values, columnHeaderValues)

                csvContent[rowID] = row

            self._writeToCSV(key, columnHeaderValues, csvContent, csvPath)


class DoseStatsCollectorBatchAction(BatchActionBase):
    """Batch class for the dose collection actions."""

    def __init__(self, inputSelector, selectedStats=None, actionTag="doseStatCollector",
                 session=None, additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
        BatchActionBase.__init__(self, actionTag=actionTag, actionClass=DoseStatsCollectorAction,
                                 primaryInputSelector=inputSelector, selectedStats=selectedStats,
                                 primaryAlias='doses', splitter={'doses': BaseSplitter()}, session=session,
                                 relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps=additionalActionProps,
                                 **singleActionParameters)
