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

import os
import shutil
import unittest

from pyoneer.criteria.durationCriterion import DurationCriterion

from avid.common.artefact import defaultProps
from avid.selectors.keyValueSelector import ActionTagSelector
from pyoneer.criteria.propertyCriterion import PropertyCriterion
from pyoneer.evaluation import EvalInstanceDescriptor
from pyoneer.metrics import DefaultMetric


class TestSelectors(unittest.TestCase):

  def setUp(self):
    self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "metricsTest")
    self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "metricsTest", "testlist"+os.extsep+"avid")
    self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_metrics")
    self.testWorkflowFile = os.path.join(os.path.split(__file__)[0],"data", "metricsTest", "testworkflow"+os.extsep+"py")
              
    self.ref_caseSplit_globalResult = {'pyoneer.criteria.MetricCriterionBase.FailedInstances': 0,
                                      'pyoneer.criteria.PropertyCriterion.myProp.max': 222.0,
                                      'pyoneer.criteria.PropertyCriterion.myProp.mean': 116.5,
                                      'pyoneer.criteria.PropertyCriterion.myProp.min': 11.0,
                                      'pyoneer.criteria.PropertyCriterion.myProp.sd': 105.5,
                                      'pyoneer.criteria.PropertyCriterion.myProp.sum.max': 444.0,
                                      'pyoneer.criteria.PropertyCriterion.myProp.sum.mean': 233.0,
                                      'pyoneer.criteria.PropertyCriterion.myProp.sum.min': 22.0,
                                      'pyoneer.criteria.PropertyCriterion.myProp.sum.sd': 211.0}

    self.ref_caseNtimeSplit_globalResult = {'pyoneer.criteria.MetricCriterionBase.FailedInstances': 0,
                                           'pyoneer.criteria.PropertyCriterion.myProp.max': 222.0,
                                           'pyoneer.criteria.PropertyCriterion.myProp.mean': 116.5,
                                           'pyoneer.criteria.PropertyCriterion.myProp.min': 11.0,
                                           'pyoneer.criteria.PropertyCriterion.myProp.sd': 105.5,
                                           'pyoneer.criteria.PropertyCriterion.myProp.sum.max': 222.0,
                                           'pyoneer.criteria.PropertyCriterion.myProp.sum.mean': 116.5,
                                           'pyoneer.criteria.PropertyCriterion.myProp.sum.min': 11.0,
                                           'pyoneer.criteria.PropertyCriterion.myProp.sum.sd': 105.5}

    self.ref_modifier_globalResult = {'pyoneer.criteria.MetricCriterionBase.FailedInstances': 0,
                                           'pyoneer.criteria.PropertyCriterion.modifier1.max': 42.0,
                                           'pyoneer.criteria.PropertyCriterion.modifier1.mean': 42.0,
                                           'pyoneer.criteria.PropertyCriterion.modifier1.min': 42.0,
                                           'pyoneer.criteria.PropertyCriterion.modifier1.sd': 0.0,
                                           'pyoneer.criteria.PropertyCriterion.modifier1.sum.max': 84.0,
                                           'pyoneer.criteria.PropertyCriterion.modifier1.sum.mean': 84.0,
                                           'pyoneer.criteria.PropertyCriterion.modifier1.sum.min': 84.0,
                                           'pyoneer.criteria.PropertyCriterion.modifier1.sum.sd': 0.0}
    
    self.ref_caseSplit_instances = {EvalInstanceDescriptor({'case': 'case2'}):
                                            {'pyoneer.criteria.PropertyCriterion.myProp': [222.0, 222.0],
                                             'pyoneer.criteria.PropertyCriterion.myProp.sum': 444.0},
                                    EvalInstanceDescriptor({'case': 'case1'}):
                                            {'pyoneer.criteria.PropertyCriterion.myProp': [11.0, 11.0],
                                             'pyoneer.criteria.PropertyCriterion.myProp.sum': 22.0}}

    self.ref_caseNtimeSplit_instances = {EvalInstanceDescriptor({'case': 'case1', 'timePoint': 0}):
                                          {'pyoneer.criteria.PropertyCriterion.myProp': [11.0],
                                           'pyoneer.criteria.PropertyCriterion.myProp.sum': 11.0},
                                         EvalInstanceDescriptor({'case': 'case1', 'timePoint': 1}):
                                          {'pyoneer.criteria.PropertyCriterion.myProp': [11.0],
                                           'pyoneer.criteria.PropertyCriterion.myProp.sum': 11.0},
                                         EvalInstanceDescriptor({'case': 'case2', 'timePoint': 0}):
                                          {'pyoneer.criteria.PropertyCriterion.myProp': [222.0],
                                           'pyoneer.criteria.PropertyCriterion.myProp.sum': 222.0},
                                         EvalInstanceDescriptor({'case': 'case2', 'timePoint': 1}):
                                          {'pyoneer.criteria.PropertyCriterion.myProp': [222.0],
                                           'pyoneer.criteria.PropertyCriterion.myProp.sum': 222.0}}

    self.ref_modifier_instances = {EvalInstanceDescriptor({'case': 'case2'}):
                                            {'pyoneer.criteria.PropertyCriterion.modifier1': [42.0, 42.0],
                                             'pyoneer.criteria.PropertyCriterion.modifier1.sum': 84.0},
                                    EvalInstanceDescriptor({'case': 'case1'}):
                                            {'pyoneer.criteria.PropertyCriterion.modifier1': [42.0, 42.0],
                                             'pyoneer.criteria.PropertyCriterion.modifier1.sum': 84.0}}

  def tearDown(self):
    try:
      shutil.rmtree(self.sessionDir)
    except:
      pass
                        
  def test_DefaultMetricEvaluate(self):
    metric = DefaultMetric([DurationCriterion(ActionTagSelector('Result')), PropertyCriterion('myProp', ActionTagSelector('Result'))], self.sessionDir, svWeights = {'pyoneer.criteria.PropertyCriterion.myProp': 0.5})
    
    result = metric.evaluate(self.testWorkflowFile, self.testArtefactFile)
    
    self.assertDictContainsSubset(self.ref_caseSplit_globalResult, result.measurements)

    for iDesc in self.ref_caseSplit_instances:
      self.assertDictContainsSubset(self.ref_caseSplit_instances[iDesc], result.instanceMeasurements[iDesc])
      
    self.assertDictEqual(result.valueNames, metric.valueNames)
    self.assertDictEqual(result.valueDescriptions, metric.valueDescriptions)
      
    self.assertDictEqual(result.svWeights, {'pyoneer.criteria.PropertyCriterion.myProp': 0.5})
    self.assertEqual(result.workflowFile, self.testWorkflowFile)
    self.assertEqual(result.artefactFile, self.testArtefactFile)
    self.assertEqual(result.workflowModifier, dict())
    
  def test_DefaultMetricEvaluate_modifier(self):
    metric = DefaultMetric([DurationCriterion(ActionTagSelector('Result')), PropertyCriterion('modifier1', ActionTagSelector('Result'))], self.sessionDir)
    
    result = metric.evaluate(self.testWorkflowFile, self.testArtefactFile, workflowModifier = {'modifier1': 42})
    
    self.assertDictContainsSubset(self.ref_modifier_globalResult, result.measurements)

    for iDesc in self.ref_modifier_instances:
      self.assertDictContainsSubset(self.ref_modifier_instances[iDesc], result.instanceMeasurements[iDesc])
          
    self.assertEqual(result.workflowFile, self.testWorkflowFile)
    self.assertEqual(result.artefactFile, self.testArtefactFile)
    self.assertDictEqual(result.workflowModifier, {'modifier1': 42})       
       
  def test_DefaultMetricEvaluate_split(self):
    metric = DefaultMetric([DurationCriterion(ActionTagSelector('Result')),
                            PropertyCriterion('myProp', ActionTagSelector('Result'))],
                            self.sessionDir, instanceDefiningProps = [defaultProps.CASE, defaultProps.TIMEPOINT])
    
    result = metric.evaluate(self.testWorkflowFile, self.testArtefactFile)
    
    self.assertDictContainsSubset(self.ref_caseNtimeSplit_globalResult, result.measurements)

    for iDesc in self.ref_caseNtimeSplit_instances:
      self.assertDictContainsSubset(self.ref_caseNtimeSplit_instances[iDesc], result.instanceMeasurements[iDesc])
      
    self.assertDictEqual(result.valueNames, metric.valueNames)
    self.assertDictEqual(result.valueDescriptions, metric.valueDescriptions)
      
    self.assertEqual(result.svWeights, None)
    self.assertEqual(result.workflowFile, self.testWorkflowFile)
    self.assertEqual(result.artefactFile, self.testArtefactFile)
    self.assertEqual(result.workflowModifier, dict())
    
           
  def test_DefaultMetric_ClearSession(self):

    #test if files are removed
    metric = DefaultMetric([PropertyCriterion('myProp', ActionTagSelector('Result'))], self.sessionDir, clearSessionDir = True)
    
    result = metric.evaluate(self.testWorkflowFile, self.testArtefactFile)
        
    self.assertFalse(os.path.exists(os.path.join(self.sessionDir,result.name)))
    self.assertFalse(os.path.exists(os.path.join(self.sessionDir,result.name+os.extsep+'avid')))

    #test if files are still there
    metric = DefaultMetric([PropertyCriterion('myProp', ActionTagSelector('Result'))], self.sessionDir, clearSessionDir = False)
    
    result = metric.evaluate(self.testWorkflowFile, self.testArtefactFile)

    self.assert_(os.path.exists(os.path.join(self.sessionDir,result.name)))
    self.assert_(os.path.exists(os.path.join(self.sessionDir,result.name+os.extsep+'avid')))

    
if __name__ == '__main__':
    unittest.main()