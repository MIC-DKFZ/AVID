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
from dlib import find_min_global

from pyoneer.optimization import OptimizerBase

logger = logging.getLogger(__name__)


class FindMinGlobalOptimizer(OptimizerBase):
    '''Pyoneer wrapper around the dlib.find_min_global optimizer.
      '''

    def __init__(self, parameterIDs, minima, maxima, maxiter=1000):
        '''Initialization of the optimizer.
        @param parameterIDs: list containg the IDs of the parameters that should be optimized
        @param minima: list (same ordering than parameterIDs) specifying the minim boundary of the search space.
        @param maxima: list (same ordering than parameterIDs) specifying the maxima boundary of the search space.
        @param maxiter: The maximum number of generations over which the entire population is evolved. The maximum number
         of function evaluations (with no polishing) is: (maxiter + 1) * popsize * len(x)
        '''
        OptimizerBase.__init__(self, parameterIDs=parameterIDs)
        self._mimima = minima
        self._maxima = maxima
        self._maxiter = maxiter
        self._bestResult = None
        self._best = None
        self._currentCandidateNR = 0

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

    def _evalCall(self, *args):
        parameters = dict()
        if not len(args)==len(self._mimima):
            raise RuntimeError(
                'Cannot evaluate candidate. Passed search position has wrong size. Search position: {}.'.format(args))

        for pos, value in enumerate(args):
            parameters[self._parameterIDs[pos]] = value

        label = "I{}".format(self._currentCandidateNR)
        results = self._evaluate(candidates={label: parameters})
        self._currentCandidateNR += 1

        resultSV = results[label].svMeasure

        if self._bestResult is None or resultSV<self._bestResult.svMeasure:
            self._bestResult = results[label]
            self._best = parameters

        return resultSV

    def _optimize(self):
        '''Starts the optimization.
        @result Returns a dict containing the best candidates found by the optimization process. Keys of the dict are the labels
        of the candidates. Values are tuples: The first tuple element is the parameter dictionary of the candidate. The
        second tuple element is the EvaluationResult of the candidate if calculated.
        '''

        position, value = find_min_global(self._evalCall, self._mimima, self._maxima, self._maxiter)

        result = dict()

        for top in self._top5:
            result[top.label] = (top.workflowModifier, top)
        return result
        return {'Best':(self._best,self._bestResult)}