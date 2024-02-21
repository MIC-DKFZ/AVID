# SPDX-FileCopyrightText: 2024, German Cancer Research Center (DKFZ), Division of Medical Image Computing (MIC)
#
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# or find it in LICENSE.txt.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from builtins import str
from builtins import range
import logging

from pyoneer.optimization import OptimizerBase

logger = logging.getLogger(__name__)

class ExhaustiveSearchOptimizer (OptimizerBase):
  '''Simple exhaustive search optimizer that samples the search space and returns the
  best found parameter set. If you define a minima of 1 a maxima of 9 and a frequency of 5, the following
  positions will be tested (1, 3, 5, 7, 9).'''
  
  def __init__(self, parameterIDs, minima, maxima, frequencies, searchMinimum = True):
    '''Initialization of the optimizer.
    @param parameterIDs: list containg the IDs of the parameters that should be optimized
    @param minima: list (same ordering than parameterIDs) specifying the minima boundary of the search space. The boundary is included.
    @param maxima: list (same ordering than parameterIDs) specifying the maxima boundary of the search space. The boundary is included.
    @param frequencies: list (same ordering than parameterIDs) specifying the frequencies that used to sample the search space.
    @param searchMinimum: indicates if the optimizer should search a minimum or maximum.
    '''
    OptimizerBase.__init__(self, parameterIDs=parameterIDs)
    self._mimima = minima
    self._maxima = maxima
    self._frequencies = frequencies
    self._best = minima
    self._bestSV = float('inf')
    self._bestResult = None
    self._searchMinimum = searchMinimum

    if not len(self._parameterIDs) == len(self._mimima):
      raise ValueError('Cannot initialize optimizer. Number of parameter keys ({}) and number of of minima ({}) differ'.format(self._parameterIDs,self._mimima))

    if not len(self._parameterIDs) == len(self._maxima):
      raise ValueError('Cannot initialize optimizer. Number of parameter keys ({}) and number of of maxima ({}) differ'.format(self._parameterIDs,self._maxima))

    for pos, value in enumerate(self._mimima):
      if value>self._maxima[pos]:
        raise ValueError(
          'Cannot initialize optimizer. At least one minimum is larger than corresponding maximum. Error index: {}.'.format(pos))

    for i in self._frequencies:
      if i<=0:
        raise ValueError(
          'Cannot initialize optimizer. At least one frequency is not larger than 0.')

  def deepSearch(self, level, position):
    if level < len(self._mimima):
      try:
        delta = (self._maxima[level] - self._mimima[level])/(self._frequencies[level]-1)
      except:
        delta = 0

      steps = [self._mimima[level]+delta*x for x in range(self._frequencies[level])]
      newposition = list(position)
      for i in steps:
        newposition[level] = i
        self.deepSearch(level+1, newposition)
    else:
      parameters = dict()
      for pos, value in enumerate(self._mimima):
        parameters[self._parameterIDs[pos]] = position[pos]

      label = str(position)
      results = self._evaluate(candidates={label:parameters})

      finding = False

      if self._searchMinimum:
        finding = results[label].svMeasure<self._bestSV
      else:
        finding = results[label].svMeasure>self._bestSV

      if finding:
        self._bestSV = results[label].svMeasure
        self._best = parameters
        self._bestResult = results[label]


  def _optimize(self):
    self.deepSearch(0,self._mimima)
    return {'Best':(self._best,self._bestResult)}