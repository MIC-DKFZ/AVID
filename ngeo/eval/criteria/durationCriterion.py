

from ..criteria import MetricCriterionBase
from avid.selectors import SelectorBase, AndSelector, ValidResultSelector
from avid.common.artefact import getArtefactProperty, defaultProps


class DurationCriterion(MetricCriterionBase):
  '''Base class for metric criterions used in evaluating avid workflow results.'''

  '''Measurement value ID for the duration.'''
  MID_Duration = 'ngeo.eval.criteria.DurationCriterion.duration'
  
  def __init__(self, inputSelector = SelectorBase()):
    MetricCriterionBase.__init__(self, valuesInfo = { self.MID_Duration: ['Duration','Duration of execution ( in [s])']})
    self.setSelectors(inputSelector = inputSelector)  

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

    duration = 0
    
    for artefact in relevantArtefacts['inputSelector']:
      try:
        duration = duration + getArtefactProperty(artefact, defaultProps.EXECUTION_DURATION)

      except:
        pass
      
    result = { self.MID_Duration : duration }

    return result
