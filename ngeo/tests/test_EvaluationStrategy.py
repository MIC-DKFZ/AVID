import unittest
import os
import avid.common.artefact.generator as artefactGenerator
import avid.common.artefact as artefact
from ngeo.eval.criteria.propertyCriterion import PropertyCriterion
from avid.selectors.keyValueSelector import CaseSelector, ActionTagSelector
from ngeo.eval.criteria import MetricCriterionBase
from ngeo.eval import EvaluationStrategy
from ngeo.eval.evaluationResult import saveEvaluationResult
from ngeo.eval.metrics import DefaultMetric
from ngeo.eval.criteria.durationCriterion import DurationCriterion


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

    saveEvaluationResult(os.path.join( self.sessionDir, 'result.eval'),result)

    result = strat.evaluate(artefactFile=self.testArtefactFile, workflowFile=self.testWorkflowFile)

    
  def test_PropertyCriterion_set(self):
      pass
#workflowModifier = {'modifier1': 42}

if __name__ == '__main__':
    unittest.main()