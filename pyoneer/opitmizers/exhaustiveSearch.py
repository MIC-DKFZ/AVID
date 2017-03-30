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

from pyoneer.opitmizers import OptimizerBase

logger = logging.getLogger(__name__)

class ExhaustiveSearchOptimizer (OptimizerBase):
  '''Simple exhaustive search optimizer that samples the search space and returns the
  best found parameter set.'''
  
  def __init__(self, evaluationCallBack, parameterIDs, minima, maxima, frequencies, searchMinimum = True):
    '''Initialization of the optimizer.
    @param evaluationCallBack: function callback that should be used to evalute candidates
    @param parameterIDs: list containg the IDs of the parameters that should be optimized
    @param minima: list (same ordering than parameterIDs) specifying the minim boundary of the search space.
    @param maxima: list (same ordering than parameterIDs) specifying the maxima boundary of the search space.
    @param frequencies: list (same ordering than parameterIDs) specifying the frequencies that used to sample the search space.
    @param searchMinimum: indicates if the optimizer shoud search a minimum or maximum.
    '''
    OptimizerBase.__init__(evaluationCallBack=evaluationCallBack, parameterIDs=parameterIDs)
    self._mimima = minima
    self._maxima = maxima
    self._frequencies = frequencies
    self._best = minima
    self._bestSV = float('inf')
    self._searchMinimum = searchMinimum

    if not len(self._parameterIDs) == len(self._mimima):
      raise ValueError('Cannot initialize optimizer. Number of parameter keys ({}) and number of of minima ({}) differ'.format(self._parameterIDs,self._mimima))

    if not len(self._parameterIDs) == len(self._maxima):
      raise ValueError('Cannot initialize optimizer. Number of parameter keys ({}) and number of of maxima ({}) differ'.format(self._parameterIDs,self._maxima))

    for pos in enumerate(self._mimima):
      if self._mimima[pos]>self._maxima[pos]:
        raise ValueError(
          'Cannot initialize optimizer. At least one minimum is larger than corresponding maximum. Error index: {}.'.format(pos))

    for i in self._frequencies:
      if i<=0:
        raise ValueError(
          'Cannot initialize optimizer. At least one frequency is not larger than 0.')

  def deepSearch(self, level, position):
    if level < len(self._mimima):
      delta = (self._maxima[level] - self._mimima[level])/self._frequencies[level]
      for i in range(self._mimima[level], self._maxima[level], delta):
        position[level] = i
        self.deepSearch(level+1, position)
    else:
      parameters = dict()
      for pos in enumerate(self._mimima):
        parameters[self._parameterIDs[pos]] = position[pos]
      result = self._evaluate(candidates={'c1':parameters})

      finding = False

      if self._searchMinimum:
        finding = result['c1']<self._bestSV
      else:
        finding = result['c1']>self._bestSV

      if finding:
        self._bestSV = result['c1']
        self._best = parameters


  def optimize(self):
    self.deepSearch(0,self._mimima)
    return {'Best':self._best}