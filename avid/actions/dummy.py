print __package__

from ..actions import BatchActionBase
from avid.actions import SingleActionBase

class DummySingleAction(SingleActionBase):

  def __init__(self, artefacts, actionTag, alwaysDo = False, session = None):
    SingleActionBase.__init__(self, actionTag,alwaysDo,session)
    self._artefacts = artefacts
    
  def _generateName(self):
    name = "Dummy"
    return name
       
  def _indicateOutputs(self):
    return self._artefacts
    
  def _generateOutputs(self):
    pass
    

class DummyBatchAction(BatchActionBase):
  def __init__(self, artefacts, actionTag, alwaysDo = False, session = None):
    BatchActionBase.__init__(self, actionTag, alwaysDo, session = session)
    self._artefacts = artefacts
    
  def _generateActions(self):
    actions = []
    for artefact in self._artefacts:
      action = DummySingleAction([artefact],"InternAction",self._alwaysDo, self._session)
      actions.append(action)

    return actions