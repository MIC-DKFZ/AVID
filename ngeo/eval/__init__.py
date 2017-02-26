###AVIDHEADER

import uuid

class EvalInstanceDescriptor (object):
  '''Descriptor that defines an evaluation instance (so basically all workflow
    artefact that have certain values for eval instance defining properties.
    It use used to lable/identify the evaluation measurments for instances'''
  
  def __init__(self, definingValues, ID = None):
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


class EvaluationStrategy(object):
  ''' Helper object to define a EvaluationStrategy that can be used by
  execution scripts like avid evaluation or optimization. It is simelar to 
  the TestCase class of the unittest package. ngeo execution scripts will search
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

  def evaluate(self, workflowFile, artefactFile, workflowModifier = {}):
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
    '''
    metric = self.defineMetric()
    name = self.defineName()
    
    result = metric.evaluate(workflowFile, artefactFile, workflowModifier, name)
    
    return result
