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

class OptimizationHelper (object):
  '''Helper class to run an optimization.'''
  
  def __init__(self):



class OptimizationStrategy(object):
  ''' Helper object to define a OptimizatoinStrategy that can be used by
  execution scripts like avid optimization. It is simelar to
  the TestCase class of the unittest package. pyoneer execution scripts will search
  for classes based on OptimizationStrategy and will use instances of them.
  '''
  def __init__(self, sessionDir, clearSessionDir = True):
    self.sessionDir = sessionDir
    self.clearSessionDir = clearSessionDir

  def defineOptimizer(self):
    '''This method must be implemented and return an optimizer instance.'''
    raise NotImplementedError("Reimplement in a derived class to function correctly.")
    pass    

  def defineName(self):
    '''This method returns the name of the optimization strategy. It can be
     reimplemented to specify the name of the strategy.'''
    return "Unnamed Optimization"

  def optimumIsMinimum(self):
    '''This method indicates if the optimum is a minimum(return True) and therefore lesser values (sv measurement or
     weighted measurements) are better. If it returns False the optimum is a maximum. The default implementation returns
     True. Reimplment the method for a strategy if you want to change it.'''
    return True

  def evaluate(self, workflowFile, artefactFile, workflowModifier = {}, label = None):
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
    
    result = metric.evaluate(workflowFile, artefactFile, workflowModifier=workflowModifier, label=label)
    
    return result
