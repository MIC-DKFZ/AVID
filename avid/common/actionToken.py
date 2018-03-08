# AVID
# Automated workflow system for cohort analysis in radiology and radiation therapy
#
# Copyright (c) German Cancer Research Center,
# Software development for Integrated Diagnostic and Therapy (SIDT).
# All rights reserved.
#
# This software is distributed WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.
#
# See LICENSE.txt or http://www.dkfz.de/en/sidt/index.html for details.

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
