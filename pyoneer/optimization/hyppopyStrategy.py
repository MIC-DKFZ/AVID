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

from pyoneer.optimization.hyppopyWrapper import HyppopyOptimizer
from pyoneer.optimization.strategy import OptimizationStrategy


class HyppopyPoolStrategy(OptimizationStrategy):
    ''' Base class for strategies that uses hyppopy (and its solver pool) to optimize a workflow.
        Implement defineSearchParameters() to generate the "hyperparameter" section of the hyppopy
        config dict.
        Implement defineSolverSettings() to generate the "settings" section of the hyppopy
        config dict.
    '''

    def defineSolverSettings(self):
        '''Returns the "settings" section/sub dict of the hyppopy config dict. This result will be used to properly
        configure the solver.
        '''
        raise NotImplementedError('Reimplement in derived class to function correclty')

    def defineOptimizer(self):

        params = self.defineSearchParameters()

        config = {"hyperparameter" : params,
                  "settings" : self.defineSolverSettings()}

        return HyppopyOptimizer(parameterIDs=list(params.keys()), config=config)

    def defineName(self):
        return "HyppopyPoolStrategy"


class HyppopyGridSearchStrategy(HyppopyPoolStrategy):
    ''' Base class for strategies that uses hyppopy (and its solver pool) to optimize a workflow.
        Implement defineSearchParameters() to generate the "hyperparameter" section of the hyppopy
        config dict.
        Implement defineSolverSettings() to generate the "settings" section of the hyppopy
        config dict.
    '''

    def defineSolverSettings(self):
        '''Returns the "settings" section/sub dict of the hyppopy config dict. This result will be used to properly
        configure the solver.
        '''
        return {'custom':{'use_solver': 'gridsearch'}}

    def defineName(self):
        return "HyppopyGridSearchStrategy"
