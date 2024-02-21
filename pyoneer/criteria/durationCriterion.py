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


from ..criteria import MetricCriterionBase
from avid.selectors import SelectorBase, AndSelector, ValidResultSelector
from avid.common.artefact import getArtefactProperty, defaultProps


class DurationCriterion(MetricCriterionBase):
  '''Criterion that evaluates the execution duration of workflow results.
     When evaluating an instance, it will sum up all execution duration properties
     of the input artefacts.
  '''

  '''Measurement value ID for the duration.'''
  MID_Duration = 'pyoneer.criteria.DurationCriterion.duration'
  
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
