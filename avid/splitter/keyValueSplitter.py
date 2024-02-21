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

from avid.splitter import BaseSplitter
from avid.common.demultiplexer import splitArtefact
import avid.common.artefact.defaultProps as artefactProps

class KeyValueSplitter(BaseSplitter):
  '''Splits the artefacts in such a way that all artefacts in a splitt list have the same values for all specified keys
  respectively. So it is a simelar behavour than function splitArtefact().'''
  def __init__(self, *splitArgs):
    '''@param splitArgs the function assumes that all unkown arguments passed to the function should be handeled as split
     properties keys that are used to specify the split.'''
    super().__init__()
    self._key = splitArgs

  def splitSelection(self, selection):
    return splitArtefact(selection, *self._key)

class CaseSplitter(KeyValueSplitter):
  '''Splits artefact in such a way that all artefacts of same case are in one split.'''
  def __init__(self):
    KeyValueSplitter.__init__(self, artefactProps.CASE)

class FractionSplitter(KeyValueSplitter):
  '''Splits artefact in such a way that all artefacts of same case and timepoint are in one split.'''
  def __init__(self):
    KeyValueSplitter.__init__(self, artefactProps.CASE, artefactProps.TIMEPOINT)
