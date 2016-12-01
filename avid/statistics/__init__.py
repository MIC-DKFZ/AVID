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

def mean(list):
  return sum(list)/list.__len__()

def variance(list):
  meanValue = mean(list)
  temp = 0

  for i in range(list.__len__()):
      temp += (list[i] - meanValue) * (list[i] - meanValue)
  return temp / list.__len__()