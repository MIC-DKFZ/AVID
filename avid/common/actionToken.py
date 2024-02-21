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
from avid.selectors import ActionTagSelector

ACTION_SUCCESS = "SUCCESS"
ACTION_FAILUER = "FAILURE"
ACTION_SKIPPED = "SKIPPED"

ACTION_LOG_LEVEL = 25

def boolToSuccess(boolValue):
    if boolValue is True:
        return ACTION_SUCCESS
    else:
        return ACTION_FAILUER
        
class ActionToken(object):

    def __init__(self, session, actionTag = None, instanceName = None, state = ACTION_SUCCESS):
        self.session = session
        self.actionTag = actionTag
        self.state = state
        self.actionInstanceName = instanceName
        self.generatedArtefacts = list()
        
    def isSuccess(self):
        return self.state == ACTION_SUCCESS
    
    def isFailure(self):
        return self.state == ACTION_FAILUER

    def isSkipped(self):
        return self.state == ACTION_SKIPPED
    
    def getActionTag(self):
        return self.actionTag

    def getTokenID(self):
        _id = str(self.actionInstanceName)+"@"+str(self.getActionTag()) +"@"+self.session.name     
        return _id
    
    def __str__ (self):
        return self.getTokenID()+"::"+self.state

    @property
    def tagSelector(self):
        '''Convinience method that returns a ActionTagSelector for the action token.'''
        return ActionTagSelector(self.actionTag)
