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
from builtins import object
import avid.common.workflow as workflow
from avid.common.artefact import get_all_values_of_a_property
from avid.selectors.keyValueSelector import KeyValueSelector
from avid.selectors import SelectorBase
        
class Demultiplexer(object):

  def __init__(self, propKey, selector = SelectorBase(), workflowData = None):
      
    if workflowData is None:
      #check if we have a current generated global session we can use
      if workflow.currentGeneratedSession is not None:
        self._workflowData = workflow.currentGeneratedSession.artefacts
      else:
        raise ValueError("Session passed to the action is invalid. Session is None.")
    else: 
      self._workflowData = workflowData
      
    self._propKey = propKey    
    self._selector = selector  


  def getKeyValues(self):
    return get_all_values_of_a_property(workflow_data=self._workflowData, property_key=self._propKey)
  
  def getSelectors(self):
    
    values = self.getKeyValues()
    
    result = dict()
    
    for value in values:
      result[value] = self._selector + KeyValueSelector(self._propKey, value)
      
    return result



def getSelectors(propKey, selector = SelectorBase(), workflowData = None):
  '''Convinience function to directly get selectors for a given key, selector and
  set of workflow data (artefacts list).'''
  demux = Demultiplexer(propKey, selector, workflowData)
  
  return demux.getSelectors()


def splitArtefact(inputArtefacts, *splitArgs):
    '''Convinience helper function. Takes a list of artefacts and will split them by the given list of split arguments
    /properties. The function will return a list of splitted artefact lists.
     @param splitArgs the function assumes that all unkown arguments passed to the function should be handeled as split
     properties.'''
    splittedA = [inputArtefacts.copy()]

    for splitProperty in splitArgs:
        newSplits = list()
        for oldSplits in splittedA:
            splitDict = getSelectors(str(splitProperty), workflowData=oldSplits)
            if len(splitDict) == 0:
                #split does not contain value so keep as is
                newSplits.append(oldSplits)
            else:
                for splitID in splitDict:
                    relevantSelector = splitDict[splitID]
                    relevantInputs = relevantSelector.getSelection(oldSplits)
                    newSplits.append(relevantInputs)
        splittedA = newSplits

    return splittedA