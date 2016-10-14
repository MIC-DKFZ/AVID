import os
import logging
import csv
import collections

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper
from avid.common import osChecker

from . import BatchActionBase
from . import SingleActionBase
from avid.selectors import TypeSelector
from simpleScheduler import SimpleScheduler
from avid.selectors.keyValueSelector import FormatSelector
from avid.probability.Logistic import LogisticProbabilityFunction
from avid.probability.Logistic import LogisticProbabilityFunctionEstimator
from avid import statistics

logger = logging.getLogger(__name__)

class ProspectiveDoseAnalysisSimulatorAction(SingleActionBase):
  '''Class that establishes a dose stats collection action. the result will be stored as CSV'''

  def __init__(self, doseCollector, selectedStats = None, minFraction=2, maxFraction=25, fractionStep=1, predictor="logistic",
               percentilSampling=[0.05, 0.5, 0.95], useOnlyEstimator=False,
               useAllFractionsForEstimation=True, nFractionsEstimation=10, rowKey = artefactProps.CASEINSTANCE,
               columnKey = artefactProps.TIMEPOINT,
               withHeaders = True, actionTag = "DoseStatCollector",
               alwaysDo = False, session = None, additionalActionProps = None):
    SingleActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps)
    self._doseCollector = doseCollector

    self._minFraction = minFraction
    self._maxFraction = maxFraction
    self._fractionStep = fractionStep
    self._predictor = predictor
    self._percentilSampling = percentilSampling
    self._useOnlyEstimator = useOnlyEstimator
    self._useAllFractionsForEstimation = useAllFractionsForEstimation
    self._nFractionsEstimation = nFractionsEstimation
    self._doseListAbsolute = None
    self._doseListPerFraction = None
    self._keys = selectedStats
    self._rowKey = rowKey
    self._columnKey = columnKey
    self._resultArtefacts = dict()
    self._withHeaders = withHeaders

  def _generateName(self):
    name = "prospective_dose_simulation"
    return name
      
  def _indicateOutputs(self):
    aPath = artefactHelper.getArtefactProperty(self._doseCollector,artefactProps.URL)
    self._doseListAbsolute = self._parseDoseStatsCollector(aPath, self._keys)
    self._keys = [artefactHelper.getArtefactProperty(self._doseCollector, artefactProps.DOSE_STAT)]

    self._doseListPerFraction = self._computeDifference(self._doseListAbsolute)

    name = self.instanceName

    key = self._keys[0]

    if self._doseCollector is not None:
      #for fraction in range(self._minFraction, self._maxFraction, self._fractionStep):
      artefact = self.generateArtefact(self._doseCollector)
      artefact[artefactProps.TYPE] = artefactProps.TYPE_VALUE_RESULT
      artefact[artefactProps.FORMAT] = artefactProps.FORMAT_VALUE_CSV
      artefact[artefactProps.DOSE_STAT] = str(key)

      onlyEstimatorString = str()
      if self._useOnlyEstimator:
        artefact[artefactProps.ONLY_ESTIMATOR] = "True"
        onlyEstimatorString = "_onlyEstimator"

      nFractionsForEstimation = str()
      if not self._useAllFractionsForEstimation:
        artefact[artefactProps.N_FRACTIONS_FOR_ESTIMATION] = str(self._nFractionsEstimation)
        nFractionsForEstimation = "_nFractionsForEstimation_"+ str(self._nFractionsEstimation)

      path = artefactHelper.generateArtefactPath(self._session, artefact)
      resName = artefactHelper.ensureValidPath(name + "_" + str(key) + "_" + str(self._minFraction) + "_" +
                                               str(self._maxFraction) + "_" + str(self._fractionStep) + onlyEstimatorString + nFractionsForEstimation + "." +
                                               str(artefactHelper.getArtefactProperty(artefact, artefactProps.ID))) + os.extsep + "csv"
      resName = os.path.join(path, resName)

      artefact[artefactProps.URL] = resName

      self._resultArtefacts[0] = artefact
      
    return self._resultArtefacts.values()


  def _parseDoseStatsCollector(self, filename, statsOfInterest):
    """get relevant values from file (DoseStatistics)"""
    resultContainer = self._readCSV(filename)

    doseMapOneCaseInstance = dict()

    resultContainer.pop(0)
    for row in resultContainer:
      index = row[0]
      row.pop(0)
      rowInt = map(float,row)
      doseMapOneCaseInstance[index]=rowInt
    return doseMapOneCaseInstance

  def _readCSV(self, filename):
    matrix = list()
    with open(filename, 'r') as csvFile:
      reader = csv.reader(csvFile, delimiter=';')
      for row in reader:
        matrix.append(row)

    return matrix

  def _computeDifference(self, doseMap):
    diffDict = dict()
    for key, value in doseMap.iteritems():
      lastEntry = 0
      diffInstance = list()
      for entry in value:
        if entry != 0.0:
          diffInstance.append(entry-lastEntry)
          lastEntry = entry
      diffDict[key] = diffInstance
    return diffDict


  def _generateRow(self, rowValueDict, columnHeaderValues):
    '''ensures that a row covers a certain key range. missing keys will be filled with None.
       the row will be returned as list of values'''
    result = list()
    
    for key in columnHeaderValues:
      if key in rowValueDict:
        result.append(rowValueDict[key])
      else:
        result.append(None)
        
    #@TODO Interpolation of missing values
    
    return result
    

  def _writeToCSV(self, key, columnHeaders, content, filename):
    try:
      osChecker.checkAndCreateDir(os.path.split(filename)[0])  
      with open(filename, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', lineterminator='\n')
        
        if self._withHeaders:
          writer.writerow([self._rowKey+"/" +self._columnKey] + columnHeaders)
                
        '''write given values'''
        for key, value in content.iteritems():
          orderedValues = collections.OrderedDict(sorted(value.items()))
          row = list()
          row.append(key)
          for key, value in orderedValues.iteritems():
            row.append(value)
          writer.writerow(row)
              
    except:
      print "CSV file writing error. Aborting..."
      raise

  
  def _generateOutputs(self):
    key = self._keys[0]
    predictedDoseDistributions = dict()
    csvPath = artefactHelper.getArtefactProperty(self._resultArtefacts[0],artefactProps.URL)
    for fraction in range(self._minFraction, self._maxFraction+1, self._fractionStep):

      columnHeaderValues = self._percentilSampling

      for key in self._doseListPerFraction:
        curDoseListPerFraction = self._doseListPerFraction[key]

        actualDosesToFraction = curDoseListPerFraction[:fraction]

        if not self._useAllFractionsForEstimation:
          fractionsToInclude = min([fraction, self._nFractionsEstimation])
          actualDosesToFractionForPrediction = actualDosesToFraction[-1*fractionsToInclude:]
        else:
          actualDosesToFractionForPrediction = actualDosesToFraction
        predictedDoseDistribution = dict()

        if self._predictor is 'logistic':
          probabilityFunctionEstimator = LogisticProbabilityFunctionEstimator()
        else:
          raise'predictor not implemented'

        distributionParametersEstimation = probabilityFunctionEstimator.estimateParameters(actualDosesToFractionForPrediction)

        if self._predictor is 'logistic':
          probabilityFunction = LogisticProbabilityFunction(distributionParametersEstimation)
        else:
          raise'predictor not implemented'

        for percentil in self._percentilSampling:
          sumToFraction = sum(actualDosesToFraction)
          doseEstimation = probabilityFunction.getValueForPercentil(percentil)
          remainingFractions = curDoseListPerFraction.__len__()-fraction
          if self._useOnlyEstimator:
            predictedDoseDistribution[percentil] = doseEstimation*self._maxFraction
          else:
            predictedDoseDistribution[percentil] = sumToFraction+(remainingFractions*doseEstimation)
        predictedDoseDistributions[fraction] = predictedDoseDistribution

    self._writeToCSV(key, columnHeaderValues, predictedDoseDistributions, csvPath)


class ProspectiveDoseAnalysisSimulatorBatchAction(BatchActionBase):
  '''Batch class for the dose collection actions.'''
  
  def __init__(self,  inputSelector, selectedStats = None, minFraction=2, maxFraction=25, fractionStep=1,
               predictor='logistic', percentilSampling=[0.05, 0.5, 0.95], useOnlyEstimator=False,
               useAllFractionsForEstimation=True, nFractionsEstimation=10, rowKey = 'Fractions',
               columnKey = 'Percentil', withHeaders = True, actionTag = "prospectiveDoseAnalysis", alwaysDo = False,
               session = None, additionalActionProps = None, scheduler = SimpleScheduler()):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._inputStatsCollector = inputSelector.getSelection(self._session.inData)

    self._minFraction = minFraction
    self._maxFraction = maxFraction
    self._fractionStep = fractionStep
    self._predictor = predictor
    self._percentilSampling = percentilSampling
    self._useOnlyEstimator = useOnlyEstimator
    self._useAllFractionsForEstimation = useAllFractionsForEstimation
    self._nFractionsEstimation = nFractionsEstimation
    self._rowKey = rowKey
    self._columnKey = columnKey  
    self._selectedStats = selectedStats
    self._withHeaders = withHeaders

      
  def _generateActions(self):
    #filter only type result. Other artefact types are not interesting
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT) + FormatSelector(artefactProps.FORMAT_VALUE_CSV)

    inputs = self.ensureValidArtefacts(self._inputStatsCollector, resultSelector, "input stats")
    
    global logger
    if len(inputs) == 0:
      logger.debug("Input selection contains no usable artefacts (type = result).")    
    
    actions = list()
    for input in inputs:
      action = ProspectiveDoseAnalysisSimulatorAction(input, self._selectedStats, self._minFraction, self._maxFraction,
                                                      self._fractionStep, self._predictor, self._percentilSampling,
                                                      self._useOnlyEstimator, self._useAllFractionsForEstimation,
                                                      self._nFractionsEstimation, self._rowKey,
                                                      self._columnKey, self._withHeaders, self._actionTag,
                                                      self._alwaysDo, self._session, self._additionalActionProps)
      actions.append(action)
    
    return actions
