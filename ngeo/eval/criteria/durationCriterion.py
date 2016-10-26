

from criteria import MetricCriterionBase
from avid.selectors import SelectorBase, AndSelector
from avid.common.artefact import getArtefactProperty, defaultProps


class DurationCriterion(MetricCriterionBase):
  '''Base class for metric criterions used in evaluating avid workflow results.'''

  '''Measurement value ID for the duration.'''
  MID_Duration = __class__.__name__+'duration'
  
  def __init__(self, inputSelector = SelectorBase()):
    self.setSelectors(inputSelector = AndSelector(artefactSelector,Val)  
    MetricCriterionBase.__init__(self, valuesInfo = { MID_Duration: ['Duration','Duration of execution ( in [s])']})
    
    pass

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
      
    return duration
