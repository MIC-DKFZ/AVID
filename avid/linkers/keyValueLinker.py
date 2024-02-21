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

from avid.linkers import InnerLinkerBase

import avid.common.artefact.defaultProps as artefactProps

class KeyValueLinker(InnerLinkerBase):
  '''
      Links data based on the value of a given key.
  '''
  def __init__(self, key, allowOnlyFullLinkage = True, performInternalLinkage=False):
    '''@param key The key of the artefacts that should be used to compare the values.
       For details of the other paramerter, see base class.
    '''
    InnerLinkerBase.__init__(self, allowOnlyFullLinkage=allowOnlyFullLinkage,
                             performInternalLinkage=performInternalLinkage)
    self._key = key

  def _findLinkedArtefactOptions(self, primaryArtefact, secondarySelection):
    linkValue = None
    if primaryArtefact is not None and self._key in primaryArtefact:
      linkValue = primaryArtefact[self._key]

    foundArtefacts = list()

    for secondaryArtefact in secondarySelection:

      if secondaryArtefact is not None and self._key in secondaryArtefact:
        if secondaryArtefact[self._key] == linkValue:
          foundArtefacts.append(secondaryArtefact)
      else:
        if linkValue is None:
          # key does not exist, but selection value is None, therefore it is a match
          foundArtefacts.append(secondaryArtefact)

    return foundArtefacts

    
class CaseLinker(KeyValueLinker):
  '''
      Links data on the basis of the artefactProps.CASE entry 
      usually the patient information is stored in case.
  '''
  def __init__(self, allowOnlyFullLinkage = True, performInternalLinkage=False):
    KeyValueLinker.__init__(self, artefactProps.CASE, allowOnlyFullLinkage=allowOnlyFullLinkage,
                            performInternalLinkage=performInternalLinkage)

    

class TimePointLinker(KeyValueLinker):
  '''
      Links data on the basis of the artefactProps.TIMEPOINT entry.
  '''
  def __init__(self, allowOnlyFullLinkage = True, performInternalLinkage=False):
    KeyValueLinker.__init__(self, artefactProps.TIMEPOINT, allowOnlyFullLinkage=allowOnlyFullLinkage,
                            performInternalLinkage=performInternalLinkage)