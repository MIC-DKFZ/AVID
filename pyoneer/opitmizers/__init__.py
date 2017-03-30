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

import datetime
import logging
import os
import shutil
import subprocess

from pyoneer.evaluationResult import EvaluationResult

from avid.common.artefact import defaultProps
from avid.common.artefact.fileHelper import loadArtefactList_xml
from pyoneer.dataSetEvaluator import DataSetEvaluator

logger = logging.getLogger(__name__)

class OptimizerBase (object):
  '''Base class for optimizer that are used by pyoneer's optimization strategies.
   Optimizer my be concrete implementations or a wrapper arrund an optimizer to comply the pyoneer optimizer API.'''
  
  def __init__(self, evaluationCallBack, parameterIDs):
    '''Initialization of the optimizer.
    @param evaluationCallBack: function callback that should be used to evalute candidates
    @param parameterIDs: List of the IDs of the parameter that should be optimized.
    ''' 
    self._evaluationCallBack = evaluationCallBack
    self._parameterIDs = parameterIDs

  def _evaluate(self, candidates, singleValue = True):
    '''Function is called by the optimizer to evaluate the passed candidates.
    @param candidates: Dictionary containing the candidates. Keys are the string labels/IDs of the candidates. The values
    are dictionaries containing the parameters of the candidate. Keys of the parameter dict are the parameter IDs.
    @return: Returns a dict containing the measurements for the candidates. Keys of the result dict are the same as the
    candidates dict. Values depend on the parameter singleValue. If singleValue is True the result dict value is the
    single value measurement. If singleValue is False, values are the weightes measurment dict of the candidates.'''
    return self._evaluationCallBack(candidates, singleValue)

  def optimize(self):
    '''Starts the optimization.
    @result Returns a dict containing the best candidates found by the optimization process. Keys of the dict are the labels
    of the candidates. Values are the parameter dictionaries of the candidates.
    '''
    raise NotImplementedError('Reimplement in derived class to function correclty')
