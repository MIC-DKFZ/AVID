

import logging
from avid.selectors import TypeSelector
from avid.selectors import ValiditySelector
from avid.selectors import AndSelector
from avid.common.artefact import defaultProps


logger = logging.getLogger(__name__)

class MetricCriterionBase(object):
  '''Base class for metric criterions used in evaluating avid workflow results.'''
  
  def __init__(self, valuesInfo = dict()):
    '''
    @param valuesInfo: dict specifying the measurement values the criterion creates.
    Key of the dict is the ID of the value. The dict value may be a string (value name)
    or a list (1st element: value name, 2nd element (if available) value description.
    '''
    self._selectors = dict()
    self._valueNames = dict()
    self._valueDescs = dict()
            
    for id in valueInfo:
      try:
        self._valueNames[id] = str(valueInfo[id][0])
      except:
        self._valueNames[id] = str(valueInfo[id])
        
      try:
        self._valueDescs[id] = str(valueInfo[id][1])
      except:
        pass
      
    pass

  def evaluateInstance(self, instaceArtefacts):
    '''evaluates an instance/case resembled by the passed artefact list.
    @note: The selection of the artefacts is handled by derived criterion classes 
    @param instanceArtefacts: List of avid artefacts that should/could be used for the evaluation.
    @return: Returns a dictionary with the criterion measurements. Key is the
    value ID. The dict value is the measurement value(s). 
     '''
    
    relevantArtefacts = dict()
    for name in self._selectors:
      relevantArtefacts[name] = self._selectors[name].getSelection(instaceArtefacts)
    
    return _evaluateInstance(relevantArtefacts)  
    pass    

  def _evaluateInstance(self, relevantArtefacts):
    '''Internal method that realy does the evaluation regaring the passed list
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
      
  def compileSetEvaluation(self, instanceMeasures):
    '''Compiles the evaluation of the complete set using the passed instance
    measurements.
    The default implementation generates for all values of the instances the
    mean, min, max and SD. If values if instances are not a scalar but a list
    all lists of this value will be "merged" before the statistics are calculated.
    @param instanceMeasures: List of measures from calls of evaluateInstance that
    should be compiled into measurements for the whole data set.
    @return: Returns a dictionary with the criterion measurements for the whole
    set. Key is the value ID. The dict value is the measurement value(s).'''
    
    raise NotImplementedError("Reimplement in a derived class to function correctly.")
    pass    
     
  def setSelectors(self, ensureValidResults = true, **selectors):
    '''Method can be used by derived classes to register avid selectors that should be
       used to select the data for an instance evaluation.
       @param ensureValidResults: If set to true only valid result artefacts will
       be passed. This is achieved by adding result and validity selectors.'''
    for selectorName in selectors:
      aSelector = selector
      if ensureValidResults:
        aSelector = AndSelector(AndSelector(selector, ValiditySelector), TypeSelector(defaultProps.TYPE_VALUE_RESULT))
           
      self._selectors[selectorName] = aSelector
              
  @property
  def valueNames(self):
    '''Returns a dict with all valueID:valueNames of measurements the criterion generates
    when evaluating instances or whole sets. In this default implementation it
    adds for each registered value also the descreptive statistical "facets"
    (mean, max, min, std)'''
    
    result = dict()
    
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
    
    for id in self._valueDescs:
      result[id] = self._valueDescss[id]
      result[id+'.mean'] = 'Mean of' +self._valueDescs[id]
      result[id+'.min'] = 'Minimum of' +self._valueDescs[id]
      result[id+'.max'] = 'Maximum of' +self._valueDescs[id]
      result[id+'.sd'] = 'Standard deviation of' +self._valueDescs[id]
      
    return result




