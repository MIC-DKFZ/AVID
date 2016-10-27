import uuid

class EvalInstanceDescriptor (object):
  '''Descriptor that defines an evaluation instance (so basically all workflow
    artefact that have certain values for eval instance defining properties.
    It use used to lable/identify the evaluation measurments for instances'''
  
  def __init__(self, definingValues):
    self.definingValues = definingValues
    self.ID = str(uuid.uuid4())
    
  def __missing__(self, key):
    return None
   
  def __len__(self):
    return len(self.definingValues)
  
  
  def __contains__(self, key):
    return key in self.definingValues
  
  def __eq__(self,other):
    if isinstance(other, self.__class__):
      return self.definingValues == other.definingValues
    else:
      return False  

  def __ne__(self,other):
    return not self.__eq__(other)

  def __repr__(self):
    return 'EvalInstanceDescriptor(%s)' % (self.definingValues)
  def __str__(self):
    return '(%s)' % (self.definingValues)
