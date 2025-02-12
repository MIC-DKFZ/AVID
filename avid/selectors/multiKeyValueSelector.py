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
from avid.common.artefact import ArtefactCollection


class MultiKeyValueSelector(SelectorBase):
  '''
      extracts the entries of the working data, which has the specified key//value entries.
      e.g.
      key = "tag", value = "CCT"
      the selectors extracts all rows, which have a key tag, and the value is CCT.
  '''
  def __init__(self, selectionDict):
    ''' init '''
    super().__init__()
    self.__selectionDict = selectionDict

  def getKeyValueList(self):
    return self.__selectionDict   

  def setKeyValueList(self,selectionDict):
    self.__selectionDict = selectionDict
    
  def updateKeyValueDict(self,selectionDict):
    ''' adds unknown entries and replaces existing key values '''
    self.__selectionDict.update(selectionDict)

  def getSelection(self, workflowData):
    '''
        filters all entries but the entries that match the selectionDictionarry
    ''' 
    selection = workflowData
    for element in self.__selectionDict:
      selection = self.__getFilteredContainer(selection,element)
    return selection
    
  def __getFilteredContainer(self,container,dictEntry):
    outCollection = ArtefactCollection()
    try:
      for entry in container:
        if dictEntry in entry:
          if entry[dictEntry] == self.__selectionDict[dictEntry]:
            outCollection.add_artefact(entry)
        else:
          if self.__selectionDict[dictEntry] is None:
            outCollection.add_artefact(entry)
      return outCollection
    except KeyError:
      self.__workflow.getLogger().info("A key (%s) was specified, which is not stored in the input data!",dictEntry)
