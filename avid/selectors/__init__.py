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
class SelectorBase(object):
  '''
      Base class for selectors. Derive from this class to implement special
      selector versions. This class is not functional.
  '''
  def __init__(self):
    ''' init '''
    pass

  def getSelection(self, workflowData):
    '''Filters the given list of entries and returns all selected entries'''
    return workflowData #default just returns everything.
     
  def __add__(self,other):
    '''Creates an AndSelector with self and other and returns it'''
    andSelector = AndSelector(self,other)
    return andSelector
  
  
class AndSelector(SelectorBase):
  '''
      Special selector that works like an and operation on to child selectors.
      The selction result of the AndSelector is the intersection of the selection
      of both child selectors.
  '''
  def __init__(self, selector1, selector2):
    ''' init '''
    self._selector1 = selector1
    self._selector2 = selector2

  def getSelection(self, workflowData):
    '''Filters the given list of entries and returns all selected entries'''
    selection1 = self._selector1.getSelection(workflowData)
    selection2 = self._selector2.getSelection(workflowData)
    resultSelection = list(dict(),)
    for item1 in selection1:
      for item2 in selection2:
        if item1 == item2:
          resultSelection.append(item1)
          selection2.remove(item2)
          break
          
    return resultSelection

from .multiKeyValueSelector import MultiKeyValueSelector
from .keyValueSelector import KeyValueSelector
from .keyValueSelector import ActionTagSelector
from .keyValueSelector import CaseSelector
from .keyValueSelector import CaseInstanceSelector
from .keyValueSelector import FormatSelector
from .keyValueSelector import TimepointSelector
from .keyValueSelector import TypeSelector
from .keyValueSelector import ResultSelector
from .keyValueSelector import ObjectiveSelector
from .keyValueSelector import DoseStatSelector
from .validitySelector import ValiditySelector
from .keyMulitValueSelector import KeyMultiValueSelector

class ValidResultSelector(AndSelector):
  ''' Convenience selector to select all valid (!) artefacts of type result.'''
  def __init__(self):
    ''' init '''
    AndSelector.__init__(self, ValiditySelector(), ResultSelector())
