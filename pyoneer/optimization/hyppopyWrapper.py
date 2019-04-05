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

import logging

from hyppopy.SolverPool import SolverPool
from hyppopy.HyppopyProject import HyppopyProject
from hyppopy.BlackboxFunction import BlackboxFunction

from pyoneer.optimization import OptimizerBase

logger = logging.getLogger(__name__)



class HyppopyOptimizer(OptimizerBase):
    '''Pyoneer wrapper around the hyppopy solver infrastructure. By default it uses the hyppopy solver pool and everything
    is configured by the hyppopy config dictionary.'''

    def __init__(self, parameterIDs, config=None, project=None, solver=None, start_viewer = False):
        '''Initialization of the optimizer.
        @param config: hyppopy config that is used to initialize the solver. Can be ignored if project an solver are explicitly
        spacified.
        @param project: A hyppopy project instance. If None is passed it will be generated given the passed config information
        @param solver: A hyppopy solver instance. If None is passed it will be generated given the passed config information
        via the hypoppy solver pool.
        '''
        OptimizerBase.__init__(self, parameterIDs=parameterIDs)
        self._hyConfig = config
        self._hyProject = project
        self._hySolver = solver
        self._currentCandidateNR = 0
        self._top5 = list()
        self._lastEvalResult = None

        if config is None and ( project is None or solver is None):
            raise ValueError(
                'Cannot initialize optimizer. One has to pass project and solver if no config is given')

        if self._hyProject is None:
            self._hyProject = HyppopyProject(config=config)

        if self._hySolver is None:
            self._hySolver = SolverPool.get(project=self._hyProject)

        self._hySolver.blackbox = BlackboxFunction(data=self, blackbox_func = lambda data, params: data._blackBoxCall(params))


    def _blackBoxCall(self, params):
        parameters = params.copy()

        label = "I{}".format(self._currentCandidateNR)
        results = self._evaluate(candidates={label: parameters})
        self._currentCandidateNR += 1

        lastEvalResult = results[label]
        resultSV = lastEvalResult.svMeasure


        weakestPos = None
        weakestSV = float('-inf')
        for pos, top in enumerate(self._top5):
            if top[1].svMeasure>weakestSV:
                weakestPos = pos
                weakestSV = top[1].svMeasure

        if weakestSV>resultSV or len(self._top5)==0:
            self._top5.append([parameters, lastEvalResult])

        if len(self._top5)>5:
            del(self._top5[weakestPos])

        self._lastEvalResult = lastEvalResult
        return resultSV

    def _optimize(self):
        '''Starts the optimization.
        @result Returns a dict containing the best candidates found by the optimization process. Keys of the dict are the labels
        of the candidates. Values are tuples: The first tuple element is the parameter dictionary of the candidate. The
        second tuple element is the EvaluationResult of the candidate if calculated.
        '''
        self._hySolver.run()
        df, best = self._hySolver.get_results()

        evalResult = None
        for params, result in self._top5:
            if params == best:
                evalResult = result
                break

        if evalResult is None:
            logger.info("Best parameter cannot be found in the stored evaluation results; propably guessed by the solver. Trigger evaluation of the given best parameters.")
            self._blackBoxCall(best)
            evalResult = self._lastEvalResult

        return {'Best': (best, evalResult)}
