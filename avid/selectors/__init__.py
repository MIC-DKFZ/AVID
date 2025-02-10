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

from builtins import object
class SelectorBase(object):
  '''
      Base class for selectors. Selectors are used to make a selection
      of relevant artefacts. Derive from this class to implement special
      selector types. This class is not functional.
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
    super().__init__()
    self._selector1 = selector1
    self._selector2 = selector2

  def getSelection(self, workflowData):
    '''Filters the given list of entries and returns all selected entries'''
    selection1 = self._selector1.getSelection(workflowData)
    selection2 = self._selector2.getSelection(workflowData)
    resultSelection = list(dict(),)
    for item in selection1:
      if item in selection2:
        resultSelection.append(item)
          
    return resultSelection


class OrSelector(SelectorBase):
  '''
      Special selector that works like an or operation on to child selectors.
      The selction result of the OrSelector is the merge (no dublicates)
      of both child selectors.
  '''

  def __init__(self, selector1, selector2):
    ''' init '''
    super().__init__()
    self._selector1 = selector1
    self._selector2 = selector2

  def getSelection(self, workflowData):
    '''Filters the given list of entries and returns all selected entries'''
    selection1 = self._selector1.getSelection(workflowData)
    selection2 = self._selector2.getSelection(workflowData)
    resultSelection = selection1

    for item2 in selection2:
      if not item2 in resultSelection:
        resultSelection.append(item2)

    return resultSelection


class LambdaSelector(SelectorBase):
  '''
      Special selector that takes a lambda/function object and calls it to
      make the selection.
  '''

  def __init__(self, selectionFunction):
    ''' init '''
    super().__init__()
    self._selectionFunction = selectionFunction

  def getSelection(self, workflowData):
    '''Filters the given list of entries and returns all selected entries'''
    return self._selectionFunction(workflowData)


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
