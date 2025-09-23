# SPDX-FileCopyrightText: 2024, German Cancer Research Center (DKFZ), Division of Medical Image Computing (MIC)
#
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# or find it in LICENSE.txt.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from builtins import str

import avid.common.artefact.defaultProps as artefactProps
from avid.common.artefact import ArtefactCollection
from avid.selectors import SelectorBase


class KeyMultiValueSelector(SelectorBase):
  '''
      extracts the artefacts of the working data, which have one of the passed value options for the given key.
      e.g.
      key = "tag", value = "CCT", "MRI"
      the selectors extracts all artefacts, which have a key "tag", and the value "CCT" or "MRI".
  '''
  def __init__(self, key, values, negate=False, allowStringCompare=False):
    ''' init '''
    super().__init__()
    self.__key = key
    self.__values = values
    self.__allowStringCompare = allowStringCompare
    self.__negate = negate
    
  def getSelection(self, workflowData):
    '''Filters the given collection of entries and returns all selected entries'''
    outCollection = ArtefactCollection()
    
    for entry in workflowData:
      if self.__key in entry:
        if (not self.__negate and entry[self.__key] in self.__values) or (self.__negate and not entry[self.__key] in self.__values) :
          outCollection.add_artefact(entry)
        elif self.__allowStringCompare:
          validValue = entry[self.__key] is not None\
          and self.__value is not None\
          and str(entry[self.__key]) in self.__values
          
          if (not self.__negate and validValue) or (self.__negate and not validValue):
            outCollection.add_artefact(entry)
    return outCollection
  
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