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

from math import sqrt

def mean(list):
  try:
    return sum(list)/len(list)
  except:
    return None

def variance(list):
  meanValue = mean(list)
  temp = 0

  try:
    for i in range(len(list)):
        temp += (list[i] - meanValue) * (list[i] - meanValue)
    return temp / len(list)
  except:
    return None
  
def sd(list):
  var = variance(list)
  
  try:
    return sqrt(var)
  except:
    return None