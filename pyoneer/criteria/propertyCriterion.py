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

from avid.common.artefact import getArtefactProperty
from avid.selectors import SelectorBase
from pyoneer.criteria import MetricCriterionBase

logger = logging.getLogger(__name__)

class PropertyCriterion(MetricCriterionBase):
  '''Criterion that evaluates a user defined property of workflow result artefacts.
     When evaluating an instance, it will sum up all values of the specified
     property of the input artefacts. The Criterion assumes that the property
     value can be converted into a float. If not the property value will be ignored.
  '''

  '''Measurement value ID for the duration.'''
  MID_PropertyValueBase = 'pyoneer.criteria.PropertyCriterion'
    
  def __init__(self, evaluatedPropertyName, inputSelector = SelectorBase()):
    '''
    @param evaluatedPropertyName: Defines the property that should be "measured"
    by the criterion.
    '''
    self.MID_PropertyValueSum = self.MID_PropertyValueBase+'.'+evaluatedPropertyName+'.sum'
    self.MID_PropertyValues = self.MID_PropertyValueBase+'.'+evaluatedPropertyName

    MetricCriterionBase.__init__(self, valuesInfo = { self.MID_PropertyValues : [evaluatedPropertyName], self.MID_PropertyValueSum : ['Sum of '+evaluatedPropertyName]})
    
    self.setSelectors(inputSelector = inputSelector)
    self._evaluatedPropertyName = evaluatedPropertyName

  def _evaluateInstance(self, relevantArtefacts):
    values = list()
    
    for artefact in relevantArtefacts['inputSelector']:
      try:
        values.append(float(getArtefactProperty(artefact, self._evaluatedPropertyName)))
      except:
        global logger
        logger.debug('Drop property value of artefact. Cannot convert value to float. Problematic value: %s. Concerned artefact: "%s"', getArtefactProperty(artefact, self._evaluatedPropertyName), artefact)
        pass

    propsum = None
    if len(values)>0:
      propsum = sum(values)
    
    result = { self.MID_PropertyValueSum : propsum, self.MID_PropertyValues: values }

    return result