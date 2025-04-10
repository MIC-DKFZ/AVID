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

from avid.selectors import SelectorBase
import avid.common.artefact.defaultProps as artefactProps
from avid.common.artefact import getArtefactProperty, ArtefactCollection


class ValiditySelector(SelectorBase):
  ''' Convenience selector to select only artefacts that are not invalid.'''
  def __init__(self, negate=False):
    ''' init '''
    super().__init__()
    self._negate = negate
    
  def getSelection(self, workflowData):
    '''Filters the given list of entries and returns all selected entries'''
    outCollection = ArtefactCollection()
    
    for entry in workflowData:
      value = getArtefactProperty(entry, artefactProps.INVALID)
      
      if (value is not True and not self._negate) or (value is True and self._negate):
        #value may also be None and should be seen as valid.
        outCollection.add_artefact(entry)
    return outCollection
