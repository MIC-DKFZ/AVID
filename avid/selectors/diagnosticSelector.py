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
from avid.selectors import KeyValueSelector
from avid.selectors import SelectorBase
import avid.common.artefact.defaultProps as artefactProps
from avid.common.artefact import getArtefactProperty
from avid.selectors import ValiditySelector

def getInputArtefactIDs(workflowData):
  inputs = set()

  for entry in workflowData:
    value = getArtefactProperty(entry, artefactProps.INPUT_IDS)

    for ID in list(value.values()):
      inputs.add(ID)

  return list(inputs)

class IsInputSelector(SelectorBase):
  ''' Convenience selector to select only artefacts that are inputs of other artefacts in the given workflow data.'''
  def __init__(self):
    ''' init '''
    super().__init__()

  def getSelection(self, workflowData):
    '''Filters the given list of entries and returns all selected entries'''
    outList = list(dict(),)

    inputs = getInputArtefactIDs(workflowData)

    [outList.append(x) for x in workflowData if x[artefactProps.ID] in inputs]

    return outList


class IsPrimeInvalidSelector(SelectorBase):
  ''' Convenience selector to select only artefacts that are invalid but have none or valid input artefacts in the given workflow data.'''

  def __init__(self):
    ''' init '''
    super().__init__()

  def getSelection(self, workflowData):
    '''Filters the given list of entries and returns all selected entries'''

    valid_artefacts = ValiditySelector().getSelection(workflowData)

    valid_ids = [x[artefactProps.ID] for x in valid_artefacts if not x[artefactProps.INVALID]]

    outList = list(dict(),)
    for entry in workflowData:
      input_ids = getArtefactProperty(entry, artefactProps.INPUT_IDS)

      found = False
      if input_ids is not None and entry[artefactProps.INVALID]:
        found = True
        for ID in list(input_ids.values()):
          if not ID in valid_ids:
            found = False
      if found:
        outList.append(entry)

    return outList

class RootSelector(SelectorBase):
  ''' Convenience selector to select all artefacts that have no inputs.'''
  def __init__(self):
    ''' init '''
    super().__init__()

  def getSelection(self, workflowData):
    '''Filters the given list of entries and returns all selected entries'''

    outList = list(dict(),)
    for entry in workflowData:
      input_ids = getArtefactProperty(entry, artefactProps.INPUT_IDS)
      if input_ids is None or len(input_ids)==0:
        outList.append(entry)

    return outList