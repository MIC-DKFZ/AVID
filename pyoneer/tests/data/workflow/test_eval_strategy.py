from pyoneer.criteria.durationCriterion import DurationCriterion
from pyoneer.evaluation import EvaluationStrategy
from pyoneer.metrics import DefaultMetric


class myOwnEvalStrategy(EvaluationStrategy):
  
  def defineMetric(self):
    '''This method must be implemented and return an metric instance.'''
    return DefaultMetric([DurationCriterion()], self.sessionDir, clearSessionDir = self.clearSessionDir)

  def defineName(self):
    return "My Own Evaluation"
