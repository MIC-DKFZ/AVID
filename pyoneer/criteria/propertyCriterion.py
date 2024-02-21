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