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
from scipy.optimize import differential_evolution

from pyoneer.optimization import OptimizerBase

logger = logging.getLogger(__name__)


class DifferentialEvolution(OptimizerBase):
    '''Pyoneer wrapper around the scipy differential evolution optimizer.
      '''

    def __init__(self, parameterIDs, minima, maxima, strategy='best1bin', maxiter=1000, popsize=2, tol=0.01,
                 mutation=(0.5, 1), recombination=0.7):
        '''Initialization of the optimizer.
        @param parameterIDs: list containg the IDs of the parameters that should be optimized
        @param minima: list (same ordering than parameterIDs) specifying the minim boundary of the search space.
        @param maxima: list (same ordering than parameterIDs) specifying the maxima boundary of the search space.
        @param strategy: The differential evolution strategy to use. Should be one of: best1bin, best1exp, rand1exp,
                    andtobest1exp, best2exp, rand2exp, randtobest1bin, best2bin, rand2bin, rand1bin.
                    The default is "best1bin".
        @param maxiter: The maximum number of generations over which the entire population is evolved. The maximum number
         of function evaluations (with no polishing) is: (maxiter + 1) * popsize * len(x)
        @param popsize: A multiplier for setting the total population size. The population has popsize * len(x) individuals.
        @param tol: Relative tolerance for convergence, the solving stops when np.std(pop) <= atol + tol * np.abs(np.mean
        (population_energies)), where and atol and tol are the absolute and relative tolerance respectively.
        @param mutation: The mutation constant. In the literature this is also known as differential weight, being denoted
         by F. If specified as a float it should be in the range [0, 2]. If specified as a tuple (min, max) dithering is
         employed. Dithering randomly changes the mutation constant on a generation by generation basis. The mutation
         constant for that generation is taken from U[min, max). Dithering can help speed convergence significantly.
         Increasing the mutation constant increases the search radius, but will slow down convergence.
        @param recombination: The recombination constant, should be in the range [0, 1]. In the literature this is also
         known as the crossover probability, being denoted by CR. Increasing this value allows a larger number of mutants
         to progress into the next generation, but at the risk of population stability.
        '''
        OptimizerBase.__init__(self, parameterIDs=parameterIDs)
        self._mimima = minima
        self._maxima = maxima
        self._strategy = strategy
        self._maxiter = maxiter
        self._popsize = popsize
        self._tol = tol
        self._mutation = mutation
        self._recombination = recombination
        self._currentCandidateNR = 0
        self._top5 = list()

        if not len(self._parameterIDs) == len(self._mimima):
            raise ValueError(
                'Cannot initialize optimizer. Number of parameter keys ({}) and number of of minima ({}) differ'.format(
                    self._parameterIDs, self._mimima))

        if not len(self._parameterIDs) == len(self._maxima):
            raise ValueError(
                'Cannot initialize optimizer. Number of parameter keys ({}) and number of of maxima ({}) differ'.format(
                    self._parameterIDs, self._maxima))

        for pos, value in enumerate(self._mimima):
            if value > self._maxima[pos]:
                raise ValueError(
                    'Cannot initialize optimizer. At least one minimum is larger than corresponding maximum. Error index: {}.'.format(
                        pos))

    def _evalCall(self, x, *args):
        parameters = dict()
        for pos, value in enumerate(self._mimima):
            parameters[self._parameterIDs[pos]] = x[pos]

        label = "I{}".format(self._currentCandidateNR)
        results = self._evaluate(candidates={label: parameters})
        self._currentCandidateNR += 1

        resultSV = results[label].svMeasure

        weakestPos = None
        weakestSV = float('-inf')
        for pos, top in enumerate(self._top5):
            if top.svMeasure>weakestSV:
                weakestPos = pos
                weakestSV = top.svMeasure

        if weakestSV>resultSV or len(self._top5)==0:
            self._top5.append(results[label])

        if len(self._top5)>5:
            del(self._top5[weakestPos])

        return resultSV

    def _optimize(self):
        '''Starts the optimization.
        @result Returns a dict containing the best candidates found by the optimization process. Keys of the dict are the labels
        of the candidates. Values are tuples: The first tuple element is the parameter dictionary of the candidate. The
        second tuple element is the EvaluationResult of the candidate if calculated.
        '''
        bounds = list()
        for pos, min in enumerate(self._mimima):
            bounds.append((min, self._maxima[pos]))

        result = differential_evolution(self._evalCall, bounds, strategy=self._strategy, maxiter=self._maxiter,
                                        popsize=self._popsize, tol=self._tol, mutation=self._mutation,
                                        recombination=self._recombination)

        result = dict()

        for top in self._top5:
            result[top.label] = (top.workflowModifier, top)
        return result