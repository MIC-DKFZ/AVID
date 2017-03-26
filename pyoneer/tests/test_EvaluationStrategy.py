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
import unittest

from pyoneer.criteria.durationCriterion import DurationCriterion

from avid.selectors.keyValueSelector import ActionTagSelector
from pyoneer.criteria.propertyCriterion import PropertyCriterion
from pyoneer.evaluation import EvaluationStrategy
from pyoneer.metrics import DefaultMetric


class DummyStrategy(EvaluationStrategy):

    def defineMetric(self):
        '''This method must be implemented and return an metric instance.'''
        return DefaultMetric([DurationCriterion(), PropertyCriterion('modifier1', ActionTagSelector('Result')),
                              PropertyCriterion('myProp', ActionTagSelector('Result'))],
                             self.sessionDir, clearSessionDir=self.clearSessionDir)

    def defineName(self):
        return "TestEvaluation"

class TestEvaluationStrategy(unittest.TestCase):
  def setUp(self):

    self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "metricsTest")
    self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "metricsTest", "testlist"+os.extsep+"avid")
    self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary", "test_EvaluationStrategy")
    self.testWorkflowFile = os.path.join(os.path.split(__file__)[0],"data", "metricsTest", "testworkflow"+os.extsep+"py")

  def test_Evaluation(self):
    strat = DummyStrategy(self.sessionDir)

    result = strat.evaluate(artefactFile=self.testArtefactFile, workflowFile=self.testWorkflowFile)


  def test_Evaluation_withModifier(self):
    strat = DummyStrategy(self.sessionDir)

    result = strat.evaluate(artefactFile=self.testArtefactFile, workflowFile=self.testWorkflowFile, workflowModifier={'modifier1':42})

    result = strat.evaluate(artefactFile=self.testArtefactFile, workflowFile=self.testWorkflowFile)


if __name__ == '__main__':
    unittest.main()