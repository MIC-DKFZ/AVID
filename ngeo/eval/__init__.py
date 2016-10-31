import uuid

class EvalInstanceDescriptor (object):
  '''Descriptor that defines an evaluation instance (so basically all workflow
    artefact that have certain values for eval instance defining properties.
    It use used to lable/identify the evaluation measurments for instances'''
  
  def __init__(self, definingValues):
    self._definingValues = definingValues
    
    self._definingStr = str()
    
    for item in sorted(definingValues.items()):
      self._definingStr = self._definingStr+"'"+str(item[0])+"':'"+str(item[1])+"',"
      
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

class EvaluationResult (object):
  
  def __init__(self, measurements, instanceMeasurements, name = 'unknown_evaluation',
               workflowFile = '', artefactFile = '', workflowModifier = {},
               svWeights = None, valueNames = {}, valueDescriptions = {}):
    '''Init of a EvaluationResult instance.
    @param measurements: Dictionary containing the overall measurements for the
    whole test set.  
    @param instanceMeasurements: Result dictionary with measurements for each
    instance. The key of the dict is a EvalInstanceDescriptor instance,
    the value is dictionary of measurements of one instance.  
    @param name: Name/lable of this evaluation.  
    @param workflowFile: Path to the workflow script that was evaluated.  
    @param artefactFile: Path to the artefact file that used to evaluated the workflow.  
    @param workflowModifier: Dictionary of the workflow modifier used for the evaluation.
    @param svWeights: Dictionary of the weights used to calculate the single
    value measure of the evaluation.
    @param valueNames: Dictionary of the display names of used measurements.  
    @param valueDescriptions: Dictionary of the descriptions of used measurements.  
    '''  
    self.measurements = measurements
    self.instanceMeasurements = instanceMeasurements
    self.svWeights = dict()
    self.name = name
    self.workflowFile = workflowFile
    self.artefactFile = artefactFile
    self.workflowModifier = workflowModifier
    self.svWeights = svWeights
    self.valueNames = valueNames
    self.valueDescriptions = valueDescriptions
    
    
    
    