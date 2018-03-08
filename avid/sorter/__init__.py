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
class BaseSorter(object):
  '''base clase for functors used to sort a artefact list by certain criterias
  and pass back the sorted list.
  The default implementation does not touch the selection at all.'''
  def __init__(self):
    pass
  
  def sortSelection(self, selection):
    '''
    does nothing
    '''
    return selection
  
  
from .keyValueSorter import KeyValueSorter
from .timePointSorter import TimePointSorter