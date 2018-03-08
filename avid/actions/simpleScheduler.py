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

from builtins import object
class SimpleScheduler(object):
  '''Simple scheduler implementation that just executes the actions sequentially.'''
  def __init__(self):
    pass
  
  def execute(self, actionList):
    tokens = list()
    
    for action in actionList:
      tokens += action.do(False),
      
    return tokens