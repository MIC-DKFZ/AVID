class ProbabilityFunctionBase(object):
  def __init__(self, name, parameters):
    self._name = name
    self._parameters = parameters

  def getValueForPercentil(self,percentil):
    raise NotImplementedError("Reimplement in a derived class to function correctly.")
    pass

class ProbabilityFunctionEstimatorBase(object):
  def __init__(self, name):
    self._name = name
  def estimateParameters(self, list):
    raise NotImplementedError("Reimplement in a derived class to function correctly.")
    pass