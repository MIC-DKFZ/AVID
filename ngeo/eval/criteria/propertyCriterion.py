

from ngeo.eval.criteria import MetricCriterionBase
from avid.selectors import SelectorBase, AndSelector, ValidResultSelector
from avid.common.artefact import getArtefactProperty, defaultProps


class PropertyCriterion(MetricCriterionBase):
  '''Criterion that evaluates a user defined property of workflow result artefacts.
     When evaluating an instance, it will sum up all values of the specified
     property of the input artefacts. The Criterion assumes that the property
     value can be converted into a float. If not the property value will be ignored.
  '''

  '''Measurement value ID for the duration.'''
  MID_PropertyValueBase = 'ngeo.eval.criteria.PropertyCriterion'
  
  def __init__(self, evaluatedPropertyName, inputSelector = SelectorBase()):
    '''
    @param evaluatedPropertyName: Defines the property that should be "measured"
    by the criterion.
    '''
    self.MID_PropertyValue = self.MID_PropertyValueBase+'.'+evaluatedPropertyName

    MetricCriterionBase.__init__(self, valuesInfo = { self.MID_PropertyValue : [evaluatedPropertyName]})
    
    self.setSelectors(inputSelector = inputSelector)
    self._evaluatedPropertyName = evaluatedPropertyName

  def _evaluateInstance(self, relevantArtefacts):
    value = 0.0
    
    for artefact in relevantArtefacts['inputSelector']:
      try:
        value = value + float(getArtefactProperty(artefact, self._evaluatedPropertyName))
      except:
        pass
      
    result = { self.MID_PropertyValue : value }

    return result