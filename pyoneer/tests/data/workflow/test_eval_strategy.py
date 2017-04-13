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

from pyoneer.criteria.durationCriterion import DurationCriterion
from pyoneer.evaluation import EvaluationStrategy
from pyoneer.metrics import DefaultMetric

class myOwnEvalStrategy(EvaluationStrategy):
  
  def defineMetric(self):
    return DefaultMetric([DurationCriterion()], self.sessionDir, clearSessionDir = self.clearSessionDir)

  def defineName(self):
    return "My Own Evaluation"
