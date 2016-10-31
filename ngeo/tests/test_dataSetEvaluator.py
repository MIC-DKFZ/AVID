###AVIDHEADER

import unittest
import avid.common.artefact.generator as artefactGenerator
import avid.common.artefact as artefact
from ngeo.eval.criteria.durationCriterion import DurationCriterion
from ngeo.eval.criteria.propertyCriterion import PropertyCriterion
from ngeo.eval.criteria import MetricCriterionBase
from ngeo.eval.dataSetEvaluator import DataSetEvaluator
from avid.selectors.keyValueSelector import CaseSelector
from avid.common.artefact import defaultProps

class TestSelectors(unittest.TestCase):
  def setUp(self):
    self.a1 = artefactGenerator.generateArtefactEntry("Case1", None, 1, "Action1", "result", "dummy", None, execution_duration = 1)
    self.a2 = artefactGenerator.generateArtefactEntry("Case1", None, 2, "Action3", "result", "dummy", None, execution_duration = 2)
    self.a3 = artefactGenerator.generateArtefactEntry("Case2", None, 1, "Action2", "result", "dummy", None, execution_duration = 10)
    self.a4 = artefactGenerator.generateArtefactEntry("Case2", None, 2, "Action1", "result", "dummy", None, execution_duration = 20)
    self.a5 = artefactGenerator.generateArtefactEntry("Case3", None, 1, "Action1", "result", "dummy", None, execution_duration = 100)
    self.a6 = artefactGenerator.generateArtefactEntry("Case3", None, 2, "Action2", "result", "dummy", None, execution_duration = 200)
    self.a7 = artefactGenerator.generateArtefactEntry("Case3", None, 4, "Action1", "result", "dummy", None, execution_duration = 400, invalid= True)

    self.data = list()
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a1)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a2)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a3)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a4)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a5)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a6)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a7)
    
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
                        
  def test_DataSetEvaluator(self):
    evaluator = DataSetEvaluator([DurationCriterion()])
    
    result = evaluator.evaluate(self.data)
  #  self.assertDictEqual(self.instanceResultRef, result)

    evaluator = DataSetEvaluator([DurationCriterion(), PropertyCriterion(defaultProps.TIMEPOINT)])
    
    result = evaluator.evaluate(self.data)
#    self.assertDictEqual(self.instanceResultRef, result)    
    
  def test_DataSetEvaluator_multiSplit(self):
    evaluator = DataSetEvaluator([DurationCriterion()],[defaultProps.CASE, defaultProps.TIMEPOINT])
    
    result = evaluator.evaluate(self.data)
  #  self.assertDictEqual(self.instanceResultRef, result)

    evaluator = DataSetEvaluator([DurationCriterion(), PropertyCriterion(defaultProps.TIMEPOINT)],[defaultProps.CASE, defaultProps.TIMEPOINT])
    
    result = evaluator.evaluate(self.data)
 #   self.assertDictEqual(self.instanceResultRef, result) 
        
#===============================================================================
#   def test_DurationCriterion_set(self):
#     criterion = DurationCriterion()
#     
#     instanceMeasurements = list()
#     instanceMeasurements.append(criterion.evaluateInstance(self.data))
#     instanceMeasurements.append(criterion.evaluateInstance(self.data2))
# 
#     result = criterion.compileSetEvaluation(instanceMeasurements)
#     self.assertDictEqual(self.setResultRef, result, 'Check compileSetEvaluation() with normal usage')
#     
#     instanceMeasurements[1] = None
# 
#     result = criterion.compileSetEvaluation(instanceMeasurements)
#     self.assertDictEqual(self.setResultWithFailRef, result, 'Check compileSetEvaluation() with failure')
# 
#     result = criterion.compileSetEvaluation([None, None])
#     self.assertDictEqual(self.setResultFailOnlyRef, result, 'Check compileSetEvaluation() with failures only')
#  
#     result = criterion.compileSetEvaluation([])
#     self.assertDictEqual(self.setResultEmptyRef, result, 'Check compileSetEvaluation() with empty list')
# 
#   
#   def test_DurationCriterion_names(self):
#     names = DurationCriterion().valueNames
#     
#     self.assertDictEqual(names, self.namesRef)
# 
#     descs = DurationCriterion().valueDescriptions
#     
#     self.assertListEqual(names.keys(), descs.keys())
#===============================================================================

if __name__ == '__main__':
    unittest.main()