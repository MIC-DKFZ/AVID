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

import unittest

from avid.selectors import ActionTagSelector
from pyoneer.criteria import MetricCriterionBase
from pyoneer.criteria.durationCriterion import DurationCriterion

import avid.common.artefact as artefact
import avid.common.artefact.generator as artefactGenerator
from avid.common.artefact import defaultProps
from pyoneer.criteria.propertyCriterion import PropertyCriterion
from pyoneer.dataSetEvaluator import DataSetEvaluator
from pyoneer.evaluation import EvalInstanceDescriptor


class TestSelectors(unittest.TestCase):
  def setUp(self):
    self.a1 = artefactGenerator.generateArtefactEntry("Case1", None, 1, "Action1", "result", "dummy", None, execution_duration = 1)
    self.a2 = artefactGenerator.generateArtefactEntry("Case1", None, 2, "Action3", "result", "dummy", None, execution_duration = 2)
    self.a3 = artefactGenerator.generateArtefactEntry("Case2", None, 1, "Action2", "result", "dummy", None, execution_duration = 10)
    self.a4 = artefactGenerator.generateArtefactEntry("Case2", None, 2, "Action1", "result", "dummy", None, execution_duration = 20)
    self.a5 = artefactGenerator.generateArtefactEntry("Case3", None, 1, "Action1", "result", "dummy", None, execution_duration = 100)
    self.a6 = artefactGenerator.generateArtefactEntry("Case3", None, 3, "Action2", "result", "dummy", None, execution_duration = 200)
    self.a7 = artefactGenerator.generateArtefactEntry("Case3", None, 4, "Action1", "result", "dummy", None, execution_duration = 400, invalid= True)

    self.data = list()
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a1)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a2)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a3)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a4)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a5)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a6)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a7)
    
    self.instanceResultRef = {EvalInstanceDescriptor({'case': 'Case3'}): {'pyoneer.criteria.DurationCriterion.duration': 300.0},
                              EvalInstanceDescriptor({'case': 'Case2'}): {'pyoneer.criteria.DurationCriterion.duration': 30.0},
                              EvalInstanceDescriptor({'case': 'Case1'}): {'pyoneer.criteria.DurationCriterion.duration': 3.0}}

    self.instanceResultRef_2Criteria = {EvalInstanceDescriptor({'case': 'Case3'}): {'pyoneer.criteria.PropertyCriterion.timePoint': [1.0, 3.0],
                                                                                    'pyoneer.criteria.DurationCriterion.duration': 300.0,
                                                                                    'pyoneer.criteria.PropertyCriterion.timePoint.sum': 4.0},
                                        EvalInstanceDescriptor({'case': 'Case2'}): {'pyoneer.criteria.PropertyCriterion.timePoint': [1.0, 2.0],
                                                                                    'pyoneer.criteria.DurationCriterion.duration': 30.0,
                                                                                    'pyoneer.criteria.PropertyCriterion.timePoint.sum': 3.0},
                                        EvalInstanceDescriptor({'case': 'Case1'}): {'pyoneer.criteria.PropertyCriterion.timePoint': [1.0, 2.0],
                                                                                    'pyoneer.criteria.DurationCriterion.duration': 3.0,
                                                                                    'pyoneer.criteria.PropertyCriterion.timePoint.sum': 3.0}}

    self.instanceResultRef_split = {EvalInstanceDescriptor({'case': 'Case1', 'timePoint': 1}): {'pyoneer.criteria.DurationCriterion.duration': 1.0},
                                    EvalInstanceDescriptor({'case': 'Case1', 'timePoint': 2}): {'pyoneer.criteria.DurationCriterion.duration': 2.0},
                                    EvalInstanceDescriptor({'case': 'Case2', 'timePoint': 2}): {'pyoneer.criteria.DurationCriterion.duration': 20.0},
                                    EvalInstanceDescriptor({'case': 'Case3', 'timePoint': 3}): {'pyoneer.criteria.DurationCriterion.duration': 200.0},
                                    EvalInstanceDescriptor({'case': 'Case3', 'timePoint': 1}): {'pyoneer.criteria.DurationCriterion.duration': 100.0},
                                    EvalInstanceDescriptor({'case': 'Case3', 'timePoint': 4}): None,
                                    EvalInstanceDescriptor({'case': 'Case2', 'timePoint': 1}): {'pyoneer.criteria.DurationCriterion.duration': 10.0}}

    self.instanceResultRef_selector = {EvalInstanceDescriptor({'case': 'Case3', 'timePoint': 1}): {'pyoneer.criteria.DurationCriterion.duration': 100.0},
                                       EvalInstanceDescriptor({'case': 'Case1', 'timePoint': 1}): {'pyoneer.criteria.DurationCriterion.duration': 1.0},
                                       EvalInstanceDescriptor({'case': 'Case3', 'timePoint': 4}): None,
                                       EvalInstanceDescriptor({'case': 'Case2', 'timePoint': 2}): {'pyoneer.criteria.DurationCriterion.duration': 20.0}}

    self.resultRef = { DurationCriterion.MID_Duration+".mean" : 111.0,
                          DurationCriterion.MID_Duration+".min": 3.0,
                          DurationCriterion.MID_Duration+".max": 300.0,
                          DurationCriterion.MID_Duration+".sd": 134.09697983176207,
                          MetricCriterionBase.MID_FailedInstances : 0
                        }

    self.resultRef_2Criteria = {'pyoneer.criteria.PropertyCriterion.timePoint.mean': 1.6666666666666667,
                                'pyoneer.criteria.PropertyCriterion.timePoint.max': 3.0,
                                'pyoneer.criteria.DurationCriterion.duration.min': 3.0,
                                'pyoneer.criteria.PropertyCriterion.timePoint.sum.mean': 3.3333333333333335,
                                'pyoneer.criteria.DurationCriterion.duration.max': 300.0,
                                'pyoneer.criteria.PropertyCriterion.timePoint.sum.min': 3.0,
                                'pyoneer.criteria.DurationCriterion.duration.mean': 111.0,
                                'pyoneer.criteria.DurationCriterion.duration.sd': 134.09697983176207,
                                'pyoneer.criteria.PropertyCriterion.timePoint.sd': 0.74535599249993,
                                'pyoneer.criteria.PropertyCriterion.timePoint.min': 1.0,
                                'pyoneer.criteria.MetricCriterionBase.FailedInstances': 0,
                                'pyoneer.criteria.PropertyCriterion.timePoint.sum.sd': 0.4714045207910317,
                                'pyoneer.criteria.PropertyCriterion.timePoint.sum.max': 4.0}

    self.resultRef_split = {'pyoneer.criteria.DurationCriterion.duration.max': 200.0,
                            'pyoneer.criteria.DurationCriterion.duration.min': 1.0,
                            'pyoneer.criteria.DurationCriterion.duration.mean': 55.5,
                            'pyoneer.criteria.DurationCriterion.duration.sd': 73.05648499620003,
                            'pyoneer.criteria.MetricCriterionBase.FailedInstances': 1}

    self.resultRef_selector = {'pyoneer.criteria.MetricCriterionBase.FailedInstances': 1,
                               'pyoneer.criteria.DurationCriterion.duration.sd': 42.897811391983886,
                               'pyoneer.criteria.DurationCriterion.duration.mean': 40.333333333333336,
                               'pyoneer.criteria.DurationCriterion.duration.min': 1.0,
                               'pyoneer.criteria.DurationCriterion.duration.max': 100.0}


  def test_DataSetEvaluator(self):
    evaluator = DataSetEvaluator([DurationCriterion()])
    
    result, instResult = evaluator.evaluate(self.data)
    self.assertDictEqual(self.resultRef, result)
    self.assertDictEqual(self.instanceResultRef, instResult)

    evaluator = DataSetEvaluator([DurationCriterion(), PropertyCriterion(defaultProps.TIMEPOINT)])
    result, instResult = evaluator.evaluate(self.data)
    self.assertDictEqual(self.resultRef_2Criteria, result)
    self.assertDictEqual(self.instanceResultRef_2Criteria, instResult)

  def test_DataSetEvaluator_multiSplit(self):
    evaluator = DataSetEvaluator([DurationCriterion()],[defaultProps.CASE, defaultProps.TIMEPOINT])
    
    result, instResult = evaluator.evaluate(self.data)
    self.assertDictEqual(self.resultRef_split, result)
    self.assertDictEqual(self.instanceResultRef_split, instResult)

  def test_DataSetEvaluator_splitSelector(self):
      evaluator = DataSetEvaluator([DurationCriterion()], [defaultProps.CASE, defaultProps.TIMEPOINT], instanceDefiningSelector=ActionTagSelector('Action1'))

      result, instResult = evaluator.evaluate(self.data)
      self.assertDictEqual(self.resultRef_selector, result)
      self.assertDictEqual(self.instanceResultRef_selector, instResult)


if __name__ == '__main__':
    unittest.main()