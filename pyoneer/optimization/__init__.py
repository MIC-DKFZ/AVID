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

from builtins import object
import logging

logger = logging.getLogger(__name__)

class OptimizerBase (object):
  '''Base class for optimizer that are used by pyoneer's optimization strategies.
   Optimizer my be concrete implementations or a wrapper around an optimizer to comply the pyoneer optimizer API.
   To use an optimizer properly ou have to set the property evaluationCallBack
    '''
  
  def __init__(self, parameterIDs):
    '''Initialization of the optimizer.
    @param parameterIDs: List of the IDs of the parameter that should be optimized.
    '''
    self._parameterIDs = parameterIDs
    #function callback that should be used to evalute candidates
    self.evaluationCallBack = None

  def _evaluate(self, candidates):
    '''Function is called by the optimizer to evaluate the passed candidates.
    @param candidates: Dictionary containing the candidates. Keys are the string labels/IDs of the candidates. The values
    are dictionaries containing the parameters of the candidate. Keys of the parameter dict are the parameter IDs.
    @return: Returns a dict containing the EvaluationResult instances for the candidates. Keys of the result dict are
    the same as the candidates dict. Values are the corresponding EvaluationResult instances.'''
    if self.evaluationCallBack is None:
      raise RuntimeError('Cannot use optimizer. Evaluation callback property is not set.')

    return self.evaluationCallBack(candidates)

  def optimize(self):
    '''Starts the optimization.
    @result Returns a dict containing the best candidates found by the optimization process. Keys of the dict are the labels
    of the candidates. Values are tuples: The first tuple element is the parameter dictionary of the candidate. The
    second tuple element is the EvaluationResult of the candidate if calculated.
    '''
    if self.evaluationCallBack is None:
      raise RuntimeError('Cannot use optimizer. Evaluation callback property is not set.')

    return self._optimize()

  def _optimize(self):
    '''Starts the optimization.
    @result Returns a dict containing the best candidates found by the optimization process. Keys of the dict are the labels
    of the candidates. Values are tuples: The first tuple element is the parameter dictionary of the candidate. The
    second tuple element is the EvaluationResult of the candidate if calculated.
    '''
    raise NotImplementedError('Reimplement in derived class to function correclty')
