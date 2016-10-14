from . import ProbabilityFunctionBase
from . import ProbabilityFunctionEstimatorBase
from avid import statistics
import math

class LogisticProbabilityFunction(ProbabilityFunctionBase):
  def __init__(self, parameters):
    ProbabilityFunctionBase.__init__(self, "logistic", parameters)
    if parameters.__len__() == 2 and 'alpha' in parameters and 'beta' in parameters:
      pass
    else:
      raise RuntimeError("Logistic function needs parameters alpha and beta!")

  def getValueForPercentil(self, percentil):
    return self._parameters['alpha'] - self._parameters['beta']*math.log(1/percentil-1.0)

class LogisticProbabilityFunctionEstimator(ProbabilityFunctionEstimatorBase):
  def __init__(self):
    ProbabilityFunctionEstimatorBase.__init__(self, "logistic")

  def estimateParameters(self, list):
    parameterEstimate = dict()

    #compute mean and variance
    mean = statistics.mean(list)
    variance = statistics.variance(list)
    #first parameter alpha equals to mean
    parameterEstimate['alpha'] = mean
    #second parameter beta can be computed from variance
    parameterEstimate['beta'] = math.sqrt(3*variance)/math.pi

    return parameterEstimate