from ngeo.eval import EvaluationStrategy
from ngeo.eval.metrics import DefaultMetric
from ngeo.eval.criteria.durationCriterion import DurationCriterion


class myOwnEvalStrategy(EvaluationStrategy):
  
  def defineMetric(self):
    '''This method must be implemented and return an metric instance.'''
    return DefaultMetric([DurationCriterion()], self.sessionDir, clearSessionDir = self.clearSessionDir)

  def defineName(self):
    return "My Own Evaluation"
