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
from builtins import str
from builtins import object
import inspect
import uuid

class EvalInstanceDescriptor (object):
  '''Descriptor that defines an evaluation instance (so basically all workflow
    artefact that have certain values for eval instance defining properties.
    It use used to lable/identify the evaluation measurments for instances'''
  
  def __init__(self, definingValues, ID = None):
    '''@param definingValues Dictionary that containes the values that uniquely define/descripe an instance.
       @param ID ID of the instance measurement that is labeled with this EvalInstanceDescriptor. If no ID is specified
        (the default) an UID will generated.'''
    self._definingValues = definingValues
    
    self._definingStr = str()
    
    for item in sorted(definingValues.items()):
      self._definingStr = self._definingStr+"'"+str(item[0])+"':'"+str(item[1])+"',"
      
    self.ID = ID
    if self.ID is None:
      self.ID = str(uuid.uuid4())
    
  def __missing__(self, key):
    return None
   
  def __len__(self):
    return len(self._definingValues)
   
  def __contains__(self, key):
    return key in self._definingValues
  
  def __eq__(self,other):
    if isinstance(other, self.__class__):
      return self._definingValues == other._definingValues
    else:
      return False  

  def __hash__(self):
    return hash(self._definingStr)
  
  def __ne__(self,other):
    return not self.__eq__(other)

  def __repr__(self):
    return 'EvalInstanceDescriptor(%s)' % (self._definingValues)

  def __str__(self):
    return '(%s)' % (self._definingValues)

  def keys(self):
    return self._definingValues.keys()

  def __getitem__(self, key):
    if key in self._definingValues:
      return self._definingValues[key]
    raise KeyError('Unkown defining value key was requested. Key: {}; self: {}'.format(key, self))


class EvaluationStrategy(object):
  ''' Helper object to define a EvaluationStrategy that can be used by
  execution scripts like avid evaluation or optimization. It is simelar to 
  the TestCase class of the unittest package. pyoneer execution scripts will search
  for classes based on EvaluationStrategy and will use instances of them.
  '''
  def __init__(self, sessionDir, clearSessionDir = True):
    self.sessionDir = sessionDir
    self.clearSessionDir = clearSessionDir

  def defineMetric(self):
    '''This method must be implemented and return an metric instance.'''
    raise NotImplementedError("Reimplement in a derived class to function correctly.")
    pass    

  def defineName(self):
    '''This method returns the name of the evaluation strategy. It can be
     reimplemented to specify the name of the strategy.'''
    return "Unnamed Evaluation"

  def optimumIsMinimum(self):
    '''This method indicates if the optimum is a minimum(return True) and therefore lesser values (sv measurement or
     weighted measurements) are better. If it returns False the optimum is a maximum. The default implementation returns
     True. Reimplment the method for a strategy if you want to change it.'''
    return True

  def evaluate(self, workflowFile, artefactFile, workflowModifier = None, label = None):
    '''Function is called to evaluate a workflow used the passed artfact definitions
    @param workflowFile: String defining the path to the avid workflow that should
    be executed.
    @param artefactFile: String defining the path to the artefact bootstrap file
     for the workflow session that will be evaluated.
    @param workflowModifier: Dict that defines the modifier for the workflow.
    They will be passed as arguments to the workflow execution. Key is the argument
    name and the dict value the argument value. The default implementation will
    generate an cl argument signature like --<key> <value>. Thus {'a':120} will
    be "--a 120". To change this behavior, override MetricBase._generateWorkflowCall(...)
    @return: Returns a EvaluationResult instance with everything you want to know.
    @param label Label that should be used by the metric when evaluating the workflow file.
    '''
    metric = self.defineMetric()
    if label is None:
      label = self.defineName()
    
    result = metric.evaluate(workflowFile, artefactFile, workflowModifier=workflowModifier, label=label, silent = False)
    
    return result


def _predicateEvaluationStrategy(member):
  return inspect.isclass(member) and issubclass(member,
                                                EvaluationStrategy) and not member.__module__ == "pyoneer.evaluation"


def detectEvaluationStrategies(relevantFile):
  '''searches for all EvaluationStrategy derivates in the given file and passes
  back a list of the found class objects.'''

  result = list()

  import imp
  import os
  stratModule = imp.load_source(os.path.splitext(os.path.split(relevantFile)[1])[0], relevantFile)

  for member in inspect.getmembers(stratModule, _predicateEvaluationStrategy):
    result.append(member[1])

  return result


def performEvaluation(stratFile, workflowPath, artefactPath, label, sessionPath, workflowModifier = None, clearSession=True):
    '''Helper/convenience function that performes an evaluation with the given inputs and returns an evaluation result instance.
    @param stratFile: String that defines the path to the strategy file that specifies the evaluation strategy that
    should be used.
    @param workflowPath: String that defines the path to AVID workflow script that should be evaluated.
    @param artefactPath: String that defines the path to AVID artefact file that should be used to evaluate the workflow.
    @param label: Label that should be used by the metric when evaluating the workflow file and generating the result information.
    @param sessionPath: String that defines the path where the (interim) results of the evaluated workflow should be stored.
    @param workflowModifier: Dict that defines the modifier for the workflow.
    They will be passed as arguments to the workflow execution. Key is the argument
    name and the dict value the argument value. The default implementation will
    generate an cl argument signature like --<key> <value>. Thus {'a':120} will
    be "--a 120". To change this behavior, you ave to chose an appropriated metric in your evaluation strategy.
    @param clearSession: Indicates if the directory indicated by sessionPath should removed after evaluation or should be keept.
    '''
    stratClasses = detectEvaluationStrategies(stratFile)

    result = None
    if len(stratClasses)>0:
        result = stratClasses[0](sessionPath, clearSession).evaluate(workflowFile=workflowPath,
                                                                      artefactFile=artefactPath, label=label,
                                                                      workflowModifier= workflowModifier)

    return result
