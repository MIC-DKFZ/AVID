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

import imp
import logging
import os
import inspect
from avid.common.artefact import ensureValidPath

from pyoneer.evaluation import detectEvaluationStrategies

logger = logging.getLogger(__name__)

class EvaluationSchedulingBase(object):
    '''Helper class to run the evaluation of optimization candidates.'''

    def __init__(self, evaluationFile, sessionDir, workflowFile, artefactFile):
        '''@param evaluationFile: String defining the path to the file containing the evaluation
          strategy that shoud be used.
          @param sessionDir Root path for any avid sessions that will be used.
        '''
        self._sessionDir = sessionDir
        self._evaluationFile = evaluationFile
        self._workflowFile = workflowFile
        self._artefactFile = artefactFile

    def getEvaluationStrategyInstance(self):
        evalclasses = detectEvaluationStrategies(self._evaluationFile)
        if len(evalclasses) > 1:
            logger.debug(
                "Found more then one evaluation strategy in file. Will create instance of first class ({})".format(
                    evalclasses[0].__name__))

        try:
            return evalclasses[0](self._sessionDir)
        except:
            raise RuntimeError("Cannot find or instanciate evaluation strategy class. Used source file: {}.".format(
                self._evaluationFile))

    def evaluate(self, candidates):
        '''Function is called by the optimizer to evaluate the passed candidates.
        @param candidates: Dictionary containing the candidates. Keys are the string labels/IDs of the candidates. The values
        are dictionaries containing the parameters of the candidate. Keys of the parameter dict are the parameter IDs.
        @return: Returns a dict containing the EvaluationResult instances for the candidates. Keys of the result dict are
        the same as the candidates dict. Values are the corresponding EvaluationResult instances.'''

        raise ImportError('Implement this methods in derived classes.')


class SimpleEvaluationScheduling(EvaluationSchedulingBase):
    def __init__(self, evaluationFile, sessionDir, workflowFile, artefactFile):
        '''@param evaluationFile: String defining the path to the file containing the evaluation
          strategy that shoud be used.
          @param sessionDir Root path for any avid sessions that will be used.
        '''
        EvaluationSchedulingBase.__init__(self, evaluationFile=evaluationFile,sessionDir=sessionDir, workflowFile=workflowFile, artefactFile=artefactFile)

        self.evalStrategy = self.getEvaluationStrategyInstance()


    def evaluate(self, candidates):
        '''Function is called by the optimizer to evaluate the passed candidates.
        @param candidates: Dictionary containing the candidates. Keys are the string labels/IDs of the candidates. The values
        are dictionaries containing the parameters of the candidate. Keys of the parameter dict are the parameter IDs.
        @return: Returns a dict containing the EvaluationResult instances for the candidates. Keys of the result dict are
        the same as the candidates dict. Values are the corresponding EvaluationResult instances.'''

        results = dict()
        for candidateKey in candidates:
            logger.info("Evaluate candidate: {}".format(candidateKey))
            result = self.evalStrategy.evaluate(workflowFile=self._workflowFile, artefactFile=self._artefactFile, workflowModifier=candidates[candidateKey], label=candidateKey)
            results[candidateKey] = result
            logger.info("Evaluation finisched. Candidate: {}".format(candidateKey))

        return results

class OptimizationStrategy(object):
    ''' Base class for Optimization strategies.
    OptimizatoinStrategy are helper objects that can be used by
    execution scripts like avid optimization. It is simelar to
    the TestCase class of the unittest package. pyoneer execution scripts will search
    for classes based on OptimizationStrategy and will use instances of them.
    '''

    def __init__(self, evaluationFile, sessionDir):
        '''@param evaluationFile: String defining the path to the file containing the evaluation
          strategy that shoud be used.
          @param sessionDir Root path for any avid sessions that will be used.
        '''
        self.sessionDir = sessionDir
        self.evaluationFile = evaluationFile

    def defineOptimizer(self):
        '''This method must be implemented and return an optimizer instance.'''
        raise NotImplementedError("Reimplement in a derived class to function correctly.")

    def defineSearchParameters(self):
        '''This method must be implmented and return a parameter descriptor. The descriptor
        specifies the search parameter used by the optimizer.'''
        raise NotImplementedError("Reimplement in a derived class to function correctly.")

    def defineName(self):
        '''This method returns the name of the optimization strategy. It can be
         reimplemented to specify the name of the strategy.'''
        return "Unnamed Optimization"

    def defineEvaluationScheduling(self, workflowFile, artefactFile, label=None):
        '''This methos returns the scheduling strategy that should be used to evaluate candidates of an optimization step.'''
        if label is None:
            label = self.defineName()
        currentsessionDir = os.path.join(self.sessionDir,ensureValidPath(label))

        return SimpleEvaluationScheduling(sessionDir=currentsessionDir, evaluationFile=self.evaluationFile,
                                          workflowFile=workflowFile, artefactFile=artefactFile)

    def _evaluate(self, candidates, singleValue=True):
        '''Function is called by the optimizer to evaluate the passed candidates.
        @param candidates: Dictionary containing the candidates. Keys are the string labels/IDs of the candidates. The values
        are dictionaries containing the parameters of the candidate. Keys of the parameter dict are the parameter IDs.
        @return: Returns a dict containing the measurements for the candidates. Keys of the result dict are the same as the
        candidates dict. Values depend on the parameter singleValue. If singleValue is True the result dict value is the
        single value measurement. If singleValue is False, values are the weightes measurment dict of the candidates.'''

        return self._evaluationCallBack(candidates, singleValue)

    def optimize(self, workflowFile, artefactFile, label=None):
        '''Function is called to evaluate a workflow used the passed artfact definitions
        @param workflowFile: String defining the path to the avid workflow that should
        be executed.
        @param artefactFile: String defining the path to the artefact bootstrap file
         for the workflow session that will be evaluated.
        @param label Label that should be used by the metric when evaluating the workflow file.
        '''
        optimizer = self.defineOptimizer()
        evalScheduler = self.defineEvaluationScheduling(workflowFile=workflowFile, artefactFile=artefactFile)

        optimizer.evaluationCallBack = evalScheduler.evaluate

        results = optimizer.optimize();

        return results


def _predicateOptimizationStrategy(member):
    return inspect.isclass(member) and issubclass(member, OptimizationStrategy)


def detectOptimizationStrategies(relevantFile):
    '''searches for all OptimizationStrategy derivates in the given file and passes
    back a list of the found class objects.'''

    result = list()

    moduleName = 'relevant_pyoneer_strategy_search_module' #search_msearchos.path.splitext(os.path.split(relevantFile)[1])[0]
    stratModule = imp.load_source(moduleName, relevantFile)

    for member in inspect.getmembers(stratModule, _predicateOptimizationStrategy):
        if member[1].__module__ == moduleName:
            #ensures that we only get members that very originaly defined in the relevant file.
            result.append(member[1])

    return result
