import unittest
import avid.common.artefact.generator as artefactGenerator
import avid.common.artefact as artefact
from ngeo.eval.criteria.propertyCriterion import PropertyCriterion
from avid.selectors.keyValueSelector import CaseSelector
from ngeo.eval.criteria import MetricCriterionBase

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

    self.instanceResultRef = { refCriterion.MID_PropertyValue : 11}
    self.instanceResultRef2 = { refCriterion.MID_PropertyValue : 10}
    
    self.setResultRef = { refCriterion.MID_PropertyValue+".mean" : 20.5,
                          refCriterion.MID_PropertyValue+".min": 11.0,
                          refCriterion.MID_PropertyValue+".max": 30.0,
                          refCriterion.MID_PropertyValue+".sd": 9.5,
                          MetricCriterionBase.MID_FailedInstances : 0
                        }
    
    self.setResultWithFailRef = { refCriterion.MID_PropertyValue+".mean" : 11.0,
                          refCriterion.MID_PropertyValue+".min": 11.0,
                          refCriterion.MID_PropertyValue+".max": 11.0,
                          refCriterion.MID_PropertyValue+".sd": 0.0,
                          MetricCriterionBase.MID_FailedInstances : 1
                        }
    
    self.setResultFailOnlyRef = { MetricCriterionBase.MID_FailedInstances : 2  }    

    self.setResultEmptyRef = { MetricCriterionBase.MID_FailedInstances : 0  }  
    
    self.namesRef = { refCriterion.MID_PropertyValue: 'coolProp',
                      refCriterion.MID_PropertyValue+".mean" : 'coolProp (mean)',
                      refCriterion.MID_PropertyValue+".min": 'coolProp (min)',
                      refCriterion.MID_PropertyValue+".max": 'coolProp (max)',
                      refCriterion.MID_PropertyValue+".sd": 'coolProp (std dev)',
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