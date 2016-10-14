import os
import logging
import csv

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper
from avid.common import osChecker
import avid.externals.doseTool as doseTool

from . import BatchActionBase
from . import SingleActionBase
from avid.selectors import TypeSelector
from simpleScheduler import SimpleScheduler
from avid.selectors.keyValueSelector import FormatSelector

logger = logging.getLogger(__name__)


class DoseStatsCollectorAction(SingleActionBase):
  '''Class that establishes a dose stats collection action. the result will be stored as CSV'''

  def __init__(self, doseSelections, selectedStats=None, rowKey=artefactProps.CASEINSTANCE,
               columnKey=artefactProps.TIMEPOINT, baseLineSelection=None,
               withHeaders=True, actionTag="DoseStatCollector",
               alwaysDo=True, session=None, additionalActionProps=None):
    SingleActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps)
    self._doseSelections = doseSelections
    self._baseLineSelection = baseLineSelection

    self._statsMatrix = None
    self._baseLineValues = None
    self._keys = selectedStats
    self._rowKey = rowKey
    self._columnKey = columnKey
    self._rowValues = sorted(set([d[rowKey] for d in doseSelections]))
    self._columnValues = sorted(set([d[columnKey] for d in doseSelections]))
    self._resultArtefacts = dict()
    self._baseLineArtefacts = dict()
    self._withHeaders = withHeaders

  def _generateName(self):
    name = "stat_collection_" + self._rowKey + "_x_" + self._columnKey

    return name

  def indicateOutputs(self):
    self._statsMatrix = self._generateStatsMatrix()
    if self._keys is None:
      self._keys = self._statsMatrix.keys()

    if self._baseLineSelection is not None:
      self._baseLineValues = self._generateBaselineDict()

    name = self._generateName()
    basename = "baseline_" + self._rowKey + "_x_" + self._columnKey

    for key in self._keys:
      if len(self._doseSelections) > 0:
        artefact = self.generateArtefact(self._doseSelections[0])
        artefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
        artefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_CSV
        artefact[artefactProps.DOSE_STAT] = str(key)

        path = artefactHelper.generateArtefactPath(self._session, artefact)
        resName = artefactHelper.ensureValidPath(name + "_" + str(key) + "." + str(
          artefactHelper.getArtefactProperty(artefact, artefactProps.ID))) + os.extsep + "csv"
        resName = os.path.join(path, resName)

        artefact[artefactProps.URL] = resName

        self._resultArtefacts[key] = artefact

      if self._baseLineSelection is not None:
        artefact = self.generateArtefact(self._baseLineSelection)
        artefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
        artefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_CSV
        artefact[artefactProps.DOSE_STAT] = str(key)
        artefact[artefactProps.ACTIONTAG] = artefact[artefactProps.ACTIONTAG] + "_baseline"

        path = artefactHelper.generateArtefactPath(self._session, artefact)
        resName = artefactHelper.ensureValidPath(basename + "_" + str(key) + "." + str(
          artefactHelper.getArtefactProperty(artefact, artefactProps.ID))) + os.extsep + "csv"
        resName = os.path.join(path, resName)

        artefact[artefactProps.URL] = resName

        self._baseLineArtefacts[key] = artefact

    return self._resultArtefacts.values() + self._baseLineArtefacts.values()

  def _parseDoseStats(self, filename, statsOfInterest):
    """get relevant values from file (DoseStatistics)"""
    resultContainer = doseTool.loadResult(filename)

    doseMapOneFraction = {}
    if statsOfInterest is None:
      statsOfInterest = resultContainer.results.keys()  # if user hasn't defined something we take all

    for key in statsOfInterest:
      if key in resultContainer.results:
        doseMapOneFraction[key] = resultContainer.results[key].value
      else:
        logger.warning("Stat key '%s' selected by user, was not found in parsed statistic file. File: %s", key,
                       filename)

    return doseMapOneFraction

  def _generateBaselineDict(self):
    aPath = artefactHelper.getArtefactProperty(self._baseLineSelection, artefactProps.URL)
    baseContainer = doseTool.loadResult(aPath)
    result = dict()
    for key in baseContainer.results.keys():
      result[key] = baseContainer.results[key].value

    return result

  def _generateStatsMatrix(self):
    '''generates and returns a n-dimensional value matrix.
    1st dim is indexed by the dose state key values
    2nd dim is indexed by the rowKey values
    3rd dim is indexed by the columnKey values'''
    matrix = dict()

    keys = self._keys

    for artefact in self._doseSelections:
      aPath = artefactHelper.getArtefactProperty(artefact, artefactProps.URL)
      rowID = artefactHelper.getArtefactProperty(artefact, self._rowKey)
      columnID = artefactHelper.getArtefactProperty(artefact, self._columnKey)
      valueMap = self._parseDoseStats(aPath, self._keys)

      if keys is None:
        keys = valueMap.keys()  # user has not select keys -> take everything

      for key in keys:
        if key in valueMap:
          if key not in matrix:
            matrix[key] = dict()

          if rowID not in matrix[key]:
            matrix[key][rowID] = dict()

          matrix[key][rowID][columnID] = valueMap[key]

    return matrix

  def _generateRow(self, rowValueDict, columnHeaderValues):
    '''ensures that a row covers a certain key range. missing keys will be filled with None.
       the row will be returned as list of values'''
    result = list()

    for key in columnHeaderValues:
      if key in rowValueDict:
        result.append(rowValueDict[key])
      else:
        result.append(None)

    # @TODO Interpolation of missing values. Is this feature still needed?

    return result

  def _getColumnHeaderValues(self, matrix):
    headers = list()

    for key in matrix:
      rowMatrix = matrix[key]
      columnKeys = rowMatrix.keys()
      headers.extend(columnKeys)

    # ensure everything is unique and sorted
    uniqueHeaders = set(headers)
    return sorted(uniqueHeaders)

  def _writeToCSV(self, key, columnHeaders, content, filename):
    try:
      osChecker.checkAndCreateDir(os.path.split(filename)[0])
      with open(filename, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', lineterminator='\n')

        if self._withHeaders:
          writer.writerow([self._rowKey + "/" + self._columnKey] + columnHeaders)

        '''write given values'''
        for rowID in sorted(content):
          row = content[rowID]
          if self._withHeaders:
            row = [str(rowID)] + row
          writer.writerow(row)

    except:
      print "CSV file writing error. Aborting..."
      raise

  def _generateOutputs(self):

    for key in self._keys:
      csvPath = artefactHelper.getArtefactProperty(self._resultArtefacts[key], artefactProps.URL)
      keyMatrix = self._statsMatrix[key]
      columnHeaderValues = self._getColumnHeaderValues(keyMatrix)
      csvContent = dict()
      for rowID in sorted(keyMatrix):
        values = keyMatrix[rowID]
        row = self._generateRow(values, columnHeaderValues)

        csvContent[rowID] = row

      self._writeToCSV(key, columnHeaderValues, csvContent, csvPath)

      # baseline processing
      if self._baseLineSelection is not None:
        csvPath = artefactHelper.getArtefactProperty(self._baseLineArtefacts[key], artefactProps.URL)
        baseValue = self._baseLineValues[key]
        csvContent = dict()
        baserow = list()

        for pos in columnHeaderValues:
          baserow.append(baseValue)

        csvContent["baseline"] = baserow

        self._writeToCSV(key, columnHeaderValues, csvContent, csvPath)


class DoseStatsCollectorBatchAction(BatchActionBase):
  '''Batch class for the dose collection actions.'''

  def __init__(self, inputSelector, selectedStats=None, rowKey=artefactProps.CASEINSTANCE,
               columnKey=artefactProps.TIMEPOINT, baseLineSelector=None,
               withHeaders=True,
               actionTag="doseStatCollector", alwaysDo=True,
               session=None, additionalActionProps=None, scheduler=SimpleScheduler()):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._inputStats = inputSelector.getSelection(self._session.inData)
    self._baseline = None
    if baseLineSelector is not None:
      self._baseline = baseLineSelector.getSelection(self._session.inData)

    self._rowKey = rowKey
    self._columnKey = columnKey
    self._selectedStats = selectedStats
    self._withHeaders = withHeaders

  def _generateActions(self):
    # filter only type result. Other artefact types are not interesting
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT) + FormatSelector(artefactProps.FORMAT_VALUE_RTTB_STATS_XML)

    inputs = resultSelector.getSelection(self._inputStats)

    baseLine = None

    global logger
    if len(inputs) == 0:
      logger.debug("Input selection contains no usable artefacts (type = result).")

    try:
      baseSelection = resultSelector.getSelection(self._baseline)
      if len(baseSelection) == 0:
        logger.debug("BaseLine selection contains no usable artefacts (type = result).")
      else:
        baseLine = baseSelection[0]
        if len(baseSelection) > 1:
          logger.debug("BaseLine selection contains more then one artefact. Only use ferst artefact: %s", baseLine)
    except:
      pass

    actions = list()

    action = DoseStatsCollectorAction(inputs, self._selectedStats, self._rowKey,
                                      self._columnKey, baseLine, self._withHeaders, self._actionTag,
                                      self._alwaysDo, self._session, self._additionalActionProps)
    actions.append(action)

    return actions