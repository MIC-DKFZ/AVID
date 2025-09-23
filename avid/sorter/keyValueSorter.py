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

from avid.common.artefact import ArtefactCollection
from avid.sorter import BaseSorter


class KeyValueSorter(BaseSorter):
  '''Sorts the selection by the values of a passed property key.'''
  def __init__(self, key, reverse=False, asNumbers=False):
    '''@param asNumbers: If true the sort values will be converted to numbers before sorting and not sorted as strings.'''
    super().__init__()
    self._key = key
    self._reverse = reverse
    self._asNumbers = asNumbers
        
  def sortSelection(self, selection):
    sortedSel = None
    if self._asNumbers:
      sortedSel= ArtefactCollection(sorted(selection, key=lambda k: float(k[self._key]), reverse = self._reverse))
    else:
      sortedSel = ArtefactCollection(sorted(selection, key=lambda k: k[self._key], reverse=self._reverse))
    return sortedSel