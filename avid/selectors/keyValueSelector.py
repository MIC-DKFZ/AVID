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

from builtins import str
from avid.selectors import SelectorBase
import avid.common.artefact.defaultProps as artefactProps

class KeyValueSelector(SelectorBase):
  '''
      extracts the entries of the working data, which has the specified key//value entries.
      e.g.
      key = "tag", value = "CCT"
      the selectors extracts all rows, which have a key tag, and the value is CCT.
  '''
  def __init__(self, key, value, negate = False, allowStringCompare = False):
    ''' init '''
    self.__key = key
    self.__value = value
    self.__allowStringCompare = allowStringCompare
    self.__negate = negate
    
  def getSelection(self, workflowData):
    '''Filters the given list of entries and returns all selected entries'''
    outList = list(dict(),)
    
    for entry in workflowData:
      if self.__key in entry:
        if self.__allowStringCompare:
          validValue = entry[self.__key] is not None \
                       and self.__value is not None \
                       and str(entry[self.__key]) == str(self.__value)

          if (not self.__negate and validValue) or (self.__negate and not validValue):
            outList.append(entry)
        else:
          if (not self.__negate and entry[self.__key] == self.__value) or (self.__negate and not entry[self.__key] == self.__value) :
            outList.append(entry)
      else:
        if self.__value is None:
          #key does not exist, but selection value is None, therefore it is a match
          outList.append(entry)
    return outList
  
class ActionTagSelector(KeyValueSelector):
  ''' Convenience selector to select by a special action tag value.'''
  def __init__(self,tagValue, negate = False):
    ''' init '''
    KeyValueSelector.__init__(self, artefactProps.ACTIONTAG, tagValue, negate)

    
class CaseSelector(KeyValueSelector):
  ''' Convenience selector to select by the case id.'''
  def __init__(self,keyValue, negate = False):
    ''' init '''
    KeyValueSelector.__init__(self, artefactProps.CASE, keyValue, negate)

    
class CaseInstanceSelector(KeyValueSelector):
  ''' Convenience selector to select by the case instance id.'''
  def __init__(self,keyValue, negate = False):
    ''' init '''
    KeyValueSelector.__init__(self, artefactProps.CASEINSTANCE, keyValue, negate, True)


class TimepointSelector(KeyValueSelector):
  ''' Convenience selector to select by the timepoint.'''
  def __init__(self,keyValue, negate = False):
    ''' init '''
    KeyValueSelector.__init__(self, artefactProps.TIMEPOINT, keyValue, negate)


class TypeSelector(KeyValueSelector):
  ''' Convenience selector to select by the type.'''
  def __init__(self,keyValue, negate = False):
    ''' init '''
    KeyValueSelector.__init__(self, artefactProps.TYPE, keyValue, negate, True)

class ResultSelector(TypeSelector):
  ''' Convenience selector to select all artefacts of type result.'''
  def __init__(self, negate = False):
    ''' init '''
    TypeSelector.__init__(self, artefactProps.TYPE_VALUE_RESULT, negate)

class FormatSelector(KeyValueSelector):
  ''' Convenience selector to select by the format of the artefact file.'''
  def __init__(self,keyValue, negate = False):
    ''' init '''
    KeyValueSelector.__init__(self, artefactProps.FORMAT, keyValue, negate, True)


class ObjectiveSelector(KeyValueSelector):
  ''' Convenience selector to select by the objective of the artefact file.'''
  def __init__(self,keyValue, negate = False):
    ''' init '''
    KeyValueSelector.__init__(self, artefactProps.OBJECTIVE, keyValue, negate, True)
    
    
class DoseStatSelector(KeyValueSelector):
  ''' Convenience selector to select by the dose stat of the artefact file.'''
  def __init__(self, keyValue, negate = False):
    ''' init '''
    KeyValueSelector.__init__(self, artefactProps.DOSE_STAT, keyValue, negate, True)