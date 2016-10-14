from .__init__ import LinkerBase

class PosLinker(LinkerBase):
  ''' Links only by position. Therefore selection is slaveSelection[masterIndex].
    If masterIndex is larger then len(slaveSelection) it will be the last element
    of the slave selection.
  '''
  def __init__(self):
    pass

  def getLinkedSelection(self,masterIndex, masterSelection, slaveSelection):
    index = masterIndex
    if index > len(slaveSelection):
      index = len(slaveSelection)-1
      
    resultSelection = list(dict(),)

    if index >= 0:
      resultSelection.append(slaveSelection[index])
               
    return resultSelection        
