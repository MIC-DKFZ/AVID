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

import unittest

from pyoneer.criteria import MetricCriterionBase

import avid.common.artefact as artefact
import avid.common.artefact.generator as artefactGenerator
from avid.selectors.keyValueSelector import CaseSelector
from pyoneer.criteria.propertyCriterion import PropertyCriterion


class TestSelectors(unittest.TestCase):
  def setUp(self):
    self.a1 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action1", "result", "dummy", None, coolProp = 1)
    self.a2 = artefactGenerator.generateArtefactEntry("Case2", None, 1, "Action3", "result", "dummy", None, coolProp = 10)
    self.a3 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action2", "config", "dummy", None, coolProp = 100)
    self.a4 = artefactGenerator.generateArtefactEntry("Case2", None, 0, "Action1", "result", "dummy", None, coolProp = 1000, invalid= True)

    self.data = list()
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a1)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a2)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a3)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a4)

    self.a5 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action1", "result", "dummy", None, coolProp = 30)
    self.a6 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action2", "config", "dummy", None, coolProp = 300)
    self.a7 = artefactGenerator.generateArtefactEntry("Case2", None, 0, "Action1", "result", "dummy", None, coolProp = 3000, invalid= True)

    self.data2 = list()
    self.data2 = artefact.addArtefactToWorkflowData(self.data2, self.a5)
    self.data2 = artefact.addArtefactToWorkflowData(self.data2, self.a6)
    self.data2 = artefact.addArtefactToWorkflowData(self.data2, self.a7)
    
    refCriterion = PropertyCriterion('coolProp')

    self.instanceResultRef = { refCriterion.MID_PropertyValueSum : 11,
                               refCriterion.MID_PropertyValues: [1, 10]
                               }
    self.instanceResultRef2 = { refCriterion.MID_PropertyValueSum : 10,
                                refCriterion.MID_PropertyValues: [10]
                                }
    
    self.setResultRef = { refCriterion.MID_PropertyValueSum+".mean" : 20.5,
                          refCriterion.MID_PropertyValueSum+".min": 11.0,
                          refCriterion.MID_PropertyValueSum+".max": 30.0,
                          refCriterion.MID_PropertyValueSum+".sd": 9.5,
                          refCriterion.MID_PropertyValues + ".mean": 13.666666666666666,
                          refCriterion.MID_PropertyValues + ".min": 1.0,
                          refCriterion.MID_PropertyValues + ".max": 30.0,
                          refCriterion.MID_PropertyValues + ".sd": 12.119772641798562,
                          MetricCriterionBase.MID_FailedInstances : 0
                        }

    self.setResultWithFailRef = { refCriterion.MID_PropertyValueSum+".mean" : 11.0,
                          refCriterion.MID_PropertyValueSum+".min": 11.0,
                          refCriterion.MID_PropertyValueSum+".max": 11.0,
                          refCriterion.MID_PropertyValueSum+".sd": 0.0,
                          refCriterion.MID_PropertyValues + ".mean": 5.5,
                          refCriterion.MID_PropertyValues + ".min": 1.0,
                          refCriterion.MID_PropertyValues + ".max": 10.0,
                          refCriterion.MID_PropertyValues + ".sd": 4.5,
                          MetricCriterionBase.MID_FailedInstances : 1
                        }

    self.setResultFailOnlyRef = { MetricCriterionBase.MID_FailedInstances : 2  }

    self.setResultEmptyRef = { MetricCriterionBase.MID_FailedInstances : 0  }  
    
    self.namesRef = { refCriterion.MID_PropertyValueSum: 'Sum of coolProp',
                      refCriterion.MID_PropertyValueSum+".mean" : 'Sum of coolProp (mean)',
                      refCriterion.MID_PropertyValueSum+".min": 'Sum of coolProp (min)',
                      refCriterion.MID_PropertyValueSum+".max": 'Sum of coolProp (max)',
                      refCriterion.MID_PropertyValueSum+".sd": 'Sum of coolProp (std dev)',
                      refCriterion.MID_PropertyValues: 'coolProp',
                      refCriterion.MID_PropertyValues + ".mean": 'coolProp (mean)',
                      refCriterion.MID_PropertyValues + ".min": 'coolProp (min)',
                      refCriterion.MID_PropertyValues + ".max": 'coolProp (max)',
                      refCriterion.MID_PropertyValues + ".sd": 'coolProp (std dev)',
                      MetricCriterionBase.MID_FailedInstances : 'Failures' }

  def test_PropertyCriterion_instance(self):
    criterion = PropertyCriterion('coolProp')
    
    result = criterion.evaluateInstance(self.data)
    self.assertDictEqual(self.instanceResultRef, result)

    criterionWithCase = PropertyCriterion('coolProp', CaseSelector('Case2'))
    result = criterionWithCase.evaluateInstance(self.data)
    self.assertDictEqual(self.instanceResultRef2, result)
    
    result = criterion.evaluateInstance([])
    self.assertEqual(None, result)
    
    
  def test_PropertyCriterion_set(self):
    criterion = PropertyCriterion('coolProp')
    
    instanceMeasurements = list()
    instanceMeasurements.append(criterion.evaluateInstance(self.data))
    instanceMeasurements.append(criterion.evaluateInstance(self.data2))

    result = criterion.compileSetEvaluation(instanceMeasurements)
    self.assertDictEqual(self.setResultRef, result, 'Check compileSetEvaluation() with normal usage')
    
    instanceMeasurements[1] = None

    result = criterion.compileSetEvaluation(instanceMeasurements)
    self.assertDictEqual(self.setResultWithFailRef, result, 'Check compileSetEvaluation() with failure')

    result = criterion.compileSetEvaluation([None, None])
    self.assertDictEqual(self.setResultFailOnlyRef, result, 'Check compileSetEvaluation() with failures only')
 
    result = criterion.compileSetEvaluation([])
    self.assertDictEqual(self.setResultEmptyRef, result, 'Check compileSetEvaluation() with empty list')

  
  def test_PropertyCriterion_names(self):
    names = PropertyCriterion('coolProp').valueNames
    
    self.assertDictEqual(names, self.namesRef)


if __name__ == '__main__':
    unittest.main()