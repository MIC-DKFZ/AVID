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

import avid.common.artefact.defaultProps as artefactProps
from avid.common.artefact import (Artefact, ArtefactCollection,
                                  getArtefactProperty)
from avid.selectors import SelectorBase, ValiditySelector


def get_input_artefact_ids(workflow_data, input_keys=None):
    """Helper that gets all input artefact ids of the passed workflow_data.
    The relevant inputs can be limited by passing a list of relevant input keys."""
    inputs = set()

    for entry in workflow_data:
        inputs_dict = getArtefactProperty(entry, artefactProps.INPUT_IDS)

        if inputs_dict is not None:
            for input_key in inputs_dict:
                if input_keys is None or input_key in input_keys:
                    for ID in inputs_dict[input_key]:
                        inputs.add(ID)

    return inputs

class IsInputSelector(SelectorBase):
    """ Convenience selector to select only artefacts that are inputs of other artefacts (derived artefacts) in
     the given workflow data. You can narrow down the relevant derived artefacts by providing a derivative selector
     or specifying the input keys that are relevant. Inheritance will be checked until the specified depth, with
     depth = -1 being unrestricted."""
    def __init__(self, input_keys=None, derivative_selector=None, depth=1):
        ''' init '''
        super().__init__()
        self.input_keys = input_keys
        self.derivative_selector = derivative_selector
        self.depth = depth

    def getSelection(self, workflowData):
        '''Filters the given collection of entries and returns all selected entries'''
        outCollection = ArtefactCollection()

        relevant_data = workflowData
        if self.derivative_selector is not None:
          relevant_data = self.derivative_selector.getSelection(workflowData=workflowData)

        depth_counter = 0
        while relevant_data and depth_counter != self.depth:
            depth_counter += 1

            input_ids = get_input_artefact_ids(relevant_data, self.input_keys)
            relevant_data = [x for x in workflowData if x[artefactProps.ID] in input_ids]
            outCollection.extend(relevant_data)

        return outCollection


class IsPrimeInvalidSelector(SelectorBase):
  ''' Convenience selector to select only artefacts that are invalid but have none or valid input artefacts in the given workflow data.'''

  def __init__(self):
    ''' init '''
    super().__init__()

  def getSelection(self, workflowData):
    '''Filters the given collection of entries and returns all selected entries'''

    valid_artefacts = ValiditySelector().getSelection(workflowData)

    valid_ids = [x[artefactProps.ID] for x in valid_artefacts if not x[artefactProps.INVALID]]

    outCollection = ArtefactCollection()
    for entry in workflowData:
      input_ids = getArtefactProperty(entry, artefactProps.INPUT_IDS)

      found = entry[artefactProps.INVALID]
      if found and input_ids is not None:
        found = True
        for input_key in input_ids:
          for ID in input_ids[input_key]:
              if not ID in valid_ids:
                found = False
      if found:
        outCollection.add_artefact(entry)

    return outCollection

class RootSelector(SelectorBase):
  ''' Convenience selector to select all artefacts that have no inputs.'''
  def __init__(self):
    ''' init '''
    super().__init__()

  def getSelection(self, workflowData):
    '''Filters the given collection of entries and returns all selected entries'''

    outCollection = ArtefactCollection()
    for entry in workflowData:
      input_ids = getArtefactProperty(entry, artefactProps.INPUT_IDS)
      if input_ids is None or len(input_ids)==0:
        outCollection.add_artefact(entry)

    return outCollection
