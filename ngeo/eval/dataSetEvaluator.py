import logging
from avid.common.artefact import defaultProps
from avid.common.demultiplexer import getSelectors
from ngeo.eval import EvalInstanceDescriptor

logger = logging.getLogger(__name__)

class DataSetEvaluator (object):
  '''Helper class that can be used to evaluate a given list of workflow artefacts
  and compile the measurements of all registered criteria for all instances.
  One has to specify a list of criteria that should be used and a list of properties.
  that should be used to discriminate the instances of the passed. By default
  that instances will be defined by the 'case' property, so each case will be evaluated
  as an instance.'''
  
  def __init__(self, usedCriteria, instanceDefiningProps = [defaultProps.CASE]):
    self._usedCriteria = usedCriteria
    self._instanceDefiningProps = instanceDefiningProps
    
    
  def _doRecursiveEvaluateInstance(self, resultData, level = 0, idValues = dict()):
    '''helper method that goes through all instances and collects the results.'''
    results = dict()
    
    if level < len(self._instanceDefiningProps):
      splitSelectorsDict = getSelectors(self._instanceDefiningProps[level], workflowData = resultData)
      
      for splitValue in splitSelectorsDict:
        #go deeper
        newValues = idValues.copy()
        newValues[self._instanceDefiningProps[level]] = splitValue
        results.update(self._doRecursiveEvaluateInstance(splitSelectorsDict[splitValue].getSelection(resultData), level+1, newValues))
        
    else:
      #collect the measurements
      measurements = dict()
      
      for criterion in self._usedCriteria:
        cm = criterion.evaluateInstance(resultData)
        if not cm is None:
          measurements.update(cm)
        else:
          global logger
          logger.debug('Marked instance (%s) as failure. Reason: criterion "%s" was not able to evaluate', idValues, criterion.__class__.__name__ )
          measurements = None
          break
        
      results[EvalInstanceDescriptor(idValues)] = measurements 
      
    return results
    
      
  def evaluate(self, resultData):
    '''Evaluates the passed data.
    @param resultData: artefact list that contains the evaluation relevant of the
    workflow.
    @return: Returns a tuple. First element is the result for the whole data set
    Second element is a result dictionary for each instance. The key of the dict
    is a EvalInstanceDescriptor instance, the value is a pooled dictionary of
    all criteria evaluateInstance() results.
    '''
    
    instanceMeasures = self._doRecursiveEvaluateInstance(resultData)
    
    instanceValues = list(instanceMeasures.values())
    
    datasetMeasures = dict()
      
    for criterion in self._usedCriteria:
      datasetMeasures.update(criterion.compileSetEvaluation(instanceValues))
      
    return (datasetMeasures, instanceMeasures)
        
    