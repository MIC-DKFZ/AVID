# AVID - pyoneer
# AVID based tool for algorithmic evaluation and optimization
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

import logging
from builtins import object
from builtins import str

from avid.selectors import AndSelector
from avid.selectors import ValidResultSelector
from avid.statistics import mean
from avid.statistics import sd

logger = logging.getLogger(__name__)

class MetricCriterionBase(object):
  '''Base class for metric critera used in evaluating avid workflow results.'''

  '''Measurement value ID for the failed instances.'''
  MID_FailedInstances = 'pyoneer.criteria.MetricCriterionBase.FailedInstances'
  
  def __init__(self, valuesInfo = None):
    '''
    @param valuesInfo: dict specifying the measurement values the criterion creates.
    Key of the dict is the ID of the value. The dict value may be a string (value name)
    or a list (1st element: value name, 2nd element (if available) value description.
    '''
    self._selectors = dict()
    self._valueNames = dict()
    self._valueDescs = dict()

    if valuesInfo is not None:
      for id in valuesInfo:
        try:
          self._valueNames[id] = str(valuesInfo[id][0])
        except:
          self._valueNames[id] = str(valuesInfo[id])

        try:
          self._valueDescs[id] = str(valuesInfo[id][1])
        except:
          pass


  def evaluateInstance(self, instanceArtefacts):
    '''evaluates an instance/case represented by the passed artefact list.
    @note: The selection of the artefacts is handled by derived criterion classes 
    @param instanceArtefacts: List of avid artefacts that should/could be used for the evaluation.
    @return: Returns a dictionary with the criterion measurements. Key is the
    value ID. The dict value is the measurement value(s). If the artefacts are not
    sufficient (no data for all selectors), it will be interpreted as a failed case
    and the return will be None.
     '''
    global logger
    
    insufficientData = False
    
    relevantArtefacts = dict()
    for name in self._selectors:
      relevantArtefacts[name] = self._selectors[name].getSelection(instanceArtefacts)
      if len(relevantArtefacts[name]) == 0:
        insufficientData = True
        logger.debug('Insufficent data for instance evaluation: No data for slot "%s"',name)
    
    if insufficientData:
      logger.debug('Evaluated instance as failure due to insufficent data.')
      return None
    else:
      return self._evaluateInstance(relevantArtefacts)

  def _evaluateInstance(self, relevantArtefacts):
    '''Internal method that really does the evaluation regaring the passed list
    of relevant artefacts. It will be called by evaluateInstance(), which generates
    the passed dictionary.
    @param relevantArtefacts: dictionary of relevant artefacts (may be lists).
    The used keys are defined by the derived classes and are the variable names
    used in the setSelectors call.
    @return: Returns a dictionary with the criterion measurements. Key is the
    value ID. The dict value is the measurement value(s). 
     '''
    raise NotImplementedError("Reimplement in a derived class to function correctly.")
    pass    
      
  def compileSetEvaluation(self, instanceMeasurements):
    '''Compiles the evaluation of the complete set using the passed instance
    measurements.
    The default implementation generates for all values of the instances the
    mean, min, max and SD. If values if instances are not a scalar but a list
    all lists of this value will be "merged" before the statistics are calculated.
    @param instanceMeasurements: List of measures from calls of evaluateInstance that
    should be compiled into measurements for the whole data set.
    @return: Returns a dictionary with the criterion measurements for the whole
    set. Key is the value ID. The dict value is the measurement value(s).'''
   
    collectedData = dict()
    failureCount = 0
    
    for instance in instanceMeasurements:
      if instance is None:
        failureCount = failureCount + 1
      else:
        for valueID in instance:
          if not valueID in collectedData:
            collectedData[valueID] = list()
            
          try:
            collectedData[valueID].extend(instance[valueID])
          except:
            collectedData[valueID].append(instance[valueID])
      
    #calculate statistics for each value
    result = dict()
    for valueID in collectedData:
      try:
        result[valueID + '.mean'] = mean(collectedData[valueID])
      except:
        result[valueID + '.mean'] = None

      try:
        result[valueID+'.min'] = min(collectedData[valueID])
      except:
        result[valueID + '.min'] = None

      try:
        result[valueID + '.max'] = max(collectedData[valueID])
      except:
        result[valueID + '.max'] = None

      try:
        result[valueID + '.sd'] = sd(collectedData[valueID])
      except:
        result[valueID + '.sd'] = None

    result[self.MID_FailedInstances] = failureCount
    
    return result
     
  def setSelectors(self, ensureValidResults = True, **selectors):
    '''Method can be used by derived classes to register avid selectors that should be
       used to select the data for an instance evaluation.
       @param ensureValidResults: If set to true only valid result artefacts will
       be passed. This is achieved by adding result and validity selectors.'''
    for selectorName in selectors:
      aSelector = selectors[selectorName]
      if ensureValidResults:
        aSelector = AndSelector(selectors[selectorName], ValidResultSelector())
           
      self._selectors[selectorName] = aSelector
              
  @property
  def valueNames(self):
    '''Returns a dict with all valueID:valueNames of measurements the criterion generates
    when evaluating instances or whole sets. In this default implementation it
    adds for each registered value also the descriptive statistical "facets"
    (mean, max, min, std) and failed_instances'''
    
    result = dict()

    result[self.MID_FailedInstances] = 'Failures'
    
    for id in self._valueNames:
      result[id] = self._valueNames[id]
      result[id+'.mean'] = self._valueNames[id]+' (mean)'
      result[id+'.min'] = self._valueNames[id]+' (min)'
      result[id+'.max'] = self._valueNames[id]+' (max)'
      result[id+'.sd'] = self._valueNames[id]+' (std dev)'
      
    return result

  @property
  def valueDescriptions(self):
    '''Returns a dict with all valueID:valueDescriptions of measurements the criterion generates
    when evaluating instances or whole sets. In this default implementation it
    adds for each registered value also the descreptive statistical "facets"
    (mean, max, min, std)'''
    
    result = dict()

    result[self.MID_FailedInstances] = 'Number of failed instances in the evaluated set.'
    
    for id in self._valueDescs:
      result[id] = self._valueDescs[id]
      result[id+'.mean'] = 'Mean of' +self._valueDescs[id]
      result[id+'.min'] = 'Minimum of' +self._valueDescs[id]
      result[id+'.max'] = 'Maximum of' +self._valueDescs[id]
      result[id+'.sd'] = 'Standard deviation of' +self._valueDescs[id]
      
    return result




