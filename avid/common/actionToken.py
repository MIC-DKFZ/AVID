ACTION_SUCCESS = "SUCCESS"
ACTION_FAILUER = "FAILURE"
ACTION_SKIPPED = "SKIPPED"

ACTION_LOG_LEVEL = 25

def boolToSuccess(boolValue):
    if boolValue is True:
        return ACTION_SUCCESS
    else:
        return ACTION_FAILUER
        
class ActionToken:

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
        _id = self.actionTag    
        return _id

    def getTokenID(self):
        _id = str(self.actionInstanceName)+"@"+str(self.getActionTag()) +"@"+self.session.name     
        return _id
    
    def __str__ (self):
        return self.getTokenID()+"::"+self.state
