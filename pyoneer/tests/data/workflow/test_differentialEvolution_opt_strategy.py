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

from avid.selectors.keyValueSelector import ActionTagSelector
from pyoneer.criteria.durationCriterion import DurationCriterion
from pyoneer.criteria.propertyCriterion import PropertyCriterion
from pyoneer.evaluation import EvaluationStrategy
from pyoneer.metrics import DefaultMetric
from pyoneer.optimization.differentialEvolutionStrategy import DefaultDifferentialEvolutionStrategy
import pyoneer.optimization.parameters as param_helper

class DummyEvalStrategy(EvaluationStrategy):

    def defineMetric(self):
        '''This method must be implemented and return an metric instance.'''
        return DefaultMetric([DurationCriterion(), PropertyCriterion('myValue', ActionTagSelector('Result'))],
                             self.sessionDir,
                             measureWeights={'pyoneer.criteria.PropertyCriterion.myValue.mean':1, 'pyoneer.criteria.DurationCriterion.duration.mean':1},
                             clearSessionDir=self.clearSessionDir)
    def defineName(self):
        return "TestEvaluation"

class DummyOptimizationStrategy(DefaultDifferentialEvolutionStrategy):

    def defineSearchParameters(self):
        desc = param_helper.generateDescriptor(['x','delay'])
        param_helper.decorateMinimum(desc, 'x', -200)
        param_helper.decorateMinimum(desc, 'delay', -10)
        param_helper.decorateMaximum(desc, 'x', 200)
        param_helper.decorateMaximum(desc, 'delay', 10)
        return desc

    def defineName(self):
        return "TestDifferentialEvolutionOptimization"
