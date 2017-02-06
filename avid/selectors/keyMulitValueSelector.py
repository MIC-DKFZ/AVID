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

from avid.selectors import SelectorBase
import avid.common.artefact.defaultProps as artefactProps

class KeyMultiValueSelector(SelectorBase):
  '''
      extracts the artefacts of the working data, which have one of the passed value options for the given key.
      e.g.
      key = "tag", value = "CCT", "MRI"
      the selectors extracts all artefacts, which have a key "tag", and the value "CCT" or "MRI".
  '''
  def __init__(self, key, values, negate = False, allowStringCompare = False):
    ''' init '''
    self.__key = key
    self.__values = values
    self.__allowStringCompare = allowStringCompare
    self.__negate = negate
    
  def getSelection(self, workflowData):
    '''Filters the given list of entries and returns all selected entries'''
    outList = list(dict(),)
    
    for entry in workflowData:
      if self.__key in entry:
        if (not self.__negate and entry[self.__key] in self.__values) or (self.__negate and not entry[self.__key] in self.__values) :
          outList.append(entry)
        elif self.__allowStringCompare:
          validValue = entry[self.__key] is not None\
          and self.__value is not None\
          and str(entry[self.__key]) in self.__values
          
          if (not self.__negate and validValue) or (self.__negate and not validValue):
            outList.append(entry)
    return outList
  
class MultiActionTagSelector(KeyMultiValueSelector):
  ''' Convenience selector to select by a special action tag value.'''
  def __init__(self,tagValues, negate = False):
    ''' init '''
    KeyMultiValueSelector.__init__(self, artefactProps.ACTIONTAG, tagValues, negate)

    
class MultiCaseSelector(KeyMultiValueSelector):
  ''' Convenience selector to select by the case id.'''
  def __init__(self,propValues, negate = False):
    ''' init '''
    KeyMultiValueSelector.__init__(self, artefactProps.CASE, propValues, negate)

    
class MultiCaseInstanceSelector(KeyMultiValueSelector):
  ''' Convenience selector to select by the case instance id.'''
  def __init__(self,propValues, negate = False):
    ''' init '''
    KeyMultiValueSelector.__init__(self, artefactProps.CASEINSTANCE, propValues, negate, True)


class MultiTimepointSelector(KeyMultiValueSelector):
  ''' Convenience selector to select by the timepoint.'''
  def __init__(self,propValues, negate = False):
    ''' init '''
    KeyMultiValueSelector.__init__(self, artefactProps.TIMEPOINT, propValues, negate)


class MultiTypeSelector(KeyMultiValueSelector):
  ''' Convenience selector to select by the type.'''
  def __init__(self,propValues, negate = False):
    ''' init '''
    KeyMultiValueSelector.__init__(self, artefactProps.TYPE, propValues, negate, True)


class MultiFormatSelector(KeyMultiValueSelector):
  ''' Convenience selector to select by the format of the artefact file.'''
  def __init__(self,propValues, negate = False):
    ''' init '''
    KeyMultiValueSelector.__init__(self, artefactProps.FORMAT, propValues, negate, True)


class MultiObjectiveSelector(KeyMultiValueSelector):
  ''' Convenience selector to select by the objective of the artefact file.'''
  def __init__(self,propValues, negate = False):
    ''' init '''
    KeyMultiValueSelector.__init__(self, artefactProps.OBJECTIVE, propValues, negate, True)
    
    
class MultiStatSelector(KeyMultiValueSelector):
  ''' Convenience selector to select by the (dose) stat of the artefact file.'''
  def __init__(self, propValues, negate = False):
    ''' init '''
    KeyMultiValueSelector.__init__(self, artefactProps.DOSE_STAT, propValues, negate, True)