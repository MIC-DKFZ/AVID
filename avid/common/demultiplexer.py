import avid.common.workflow as workflow
from avid.selectors.keyValueSelector import KeyValueSelector
from avid.selectors import SelectorBase
        
class Demultiplexer:

  def __init__(self, propKey, selector = SelectorBase(), workflowData = None):
      
    if workflowData is None:
      #check if we have a current generated global session we can use
      if workflow.currentGeneratedSession is not None:
        self._workflowData = workflow.currentGeneratedSession.inData
      else:
        raise ValueError("Session passed to the action is invalid. Session is None.")
    else: 
      self._workflowData = workflowData
      
    self._propKey = propKey    
    self._selector = selector  


  def getKeyValues(self):
    relevantSelection = self._selector.getSelection(self._workflowData)
    return [d[self._propKey] for d in relevantSelection if self._propKey in d]
  
  
  def getSelectors(self):
    
    values = self.getKeyValues()
    
    result = dict()
    
    for value in values:
      result[value] = KeyValueSelector(self._propKey, value)
      
    return result



def getSelectors(propKey, selector = SelectorBase(), workflowData = None):
  '''Convinience function to directly get selectors for a given key, selector and
  set of workflow data (artefacts list).'''
  demux = Demultiplexer(propKey, selector, workflowData)
  
  return demux.getSelectors()