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
from pyoneer.criteria.durationCriterion import DurationCriterion


class TestSelectors(unittest.TestCase):
  def setUp(self):
    self.a1 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action1", "result", "dummy", None, execution_duration = 1)
    self.a2 = artefactGenerator.generateArtefactEntry("Case2", None, 1, "Action3", "result", "dummy", None, execution_duration = 10)
    self.a3 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action2", "config", "dummy", None, execution_duration = 100)
    self.a4 = artefactGenerator.generateArtefactEntry("Case2", None, 0, "Action1", "result", "dummy", None, execution_duration = 1000, invalid= True)

    self.data = list()
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a1)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a2)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a3)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a4)

    self.a5 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action1", "result", "dummy", None, execution_duration = 30)
    self.a6 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action2", "config", "dummy", None, execution_duration = 300)
    self.a7 = artefactGenerator.generateArtefactEntry("Case2", None, 0, "Action1", "result", "dummy", None, execution_duration = 3000, invalid= True)

    self.data2 = list()
    self.data2 = artefact.addArtefactToWorkflowData(self.data2, self.a5)
    self.data2 = artefact.addArtefactToWorkflowData(self.data2, self.a6)
    self.data2 = artefact.addArtefactToWorkflowData(self.data2, self.a7)
    
    self.instanceResultRef = { DurationCriterion.MID_Duration : 11}
    self.instanceResultRef2 = { DurationCriterion.MID_Duration : 10}
    
    self.setResultRef = { DurationCriterion.MID_Duration+".mean" : 20.5,
                          DurationCriterion.MID_Duration+".min": 11.0,
                          DurationCriterion.MID_Duration+".max": 30.0,
                          DurationCriterion.MID_Duration+".sd": 9.5,
                          MetricCriterionBase.MID_FailedInstances : 0
                        }
    
    self.setResultWithFailRef = { DurationCriterion.MID_Duration+".mean" : 11.0,
                          DurationCriterion.MID_Duration+".min": 11.0,
                          DurationCriterion.MID_Duration+".max": 11.0,
                          DurationCriterion.MID_Duration+".sd": 0.0,
                          MetricCriterionBase.MID_FailedInstances : 1
                        }
    
    self.setResultFailOnlyRef = { MetricCriterionBase.MID_FailedInstances : 2  }    

    self.setResultEmptyRef = { MetricCriterionBase.MID_FailedInstances : 0  }  
    
    self.namesRef = { DurationCriterion.MID_Duration: 'Duration',
                      DurationCriterion.MID_Duration+".mean" : 'Duration (mean)',
                      DurationCriterion.MID_Duration+".min": 'Duration (min)',
                      DurationCriterion.MID_Duration+".max": 'Duration (max)',
                      DurationCriterion.MID_Duration+".sd": 'Duration (std dev)',
                      MetricCriterionBase.MID_FailedInstances : 'Failures' }
                        
  def test_DurationCriterion_instance(self):
    criterion = DurationCriterion()
    
    result = criterion.evaluateInstance(self.data)
    self.assertDictEqual(self.instanceResultRef, result)

    criterionWithCase = DurationCriterion(CaseSelector('Case2'))
    result = criterionWithCase.evaluateInstance(self.data)
    self.assertDictEqual(self.instanceResultRef2, result)
    
    result = criterion.evaluateInstance([])
    self.assertEqual(None, result)
    
    
  def test_DurationCriterion_set(self):
    criterion = DurationCriterion()
    
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

  
  def test_DurationCriterion_names(self):
    names = DurationCriterion().valueNames
    
    self.assertDictEqual(names, self.namesRef)

    descs = DurationCriterion().valueDescriptions
    
    self.assertListEqual(list(names.keys()), list(descs.keys()))

if __name__ == '__main__':
    unittest.main()