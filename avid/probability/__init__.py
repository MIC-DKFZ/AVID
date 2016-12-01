# AVID
# Automated workflow system for cohort analysis in radiology and radiation therapy
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