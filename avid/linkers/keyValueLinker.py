from avid.linkers import LinkerBase

import avid.common.artefact.defaultProps as artefactProps

class KeyValueLinker(LinkerBase):
  '''
      Links data based on the value of a given key. 
  '''
  def __init__(self, key):
    self.__key = key
      
  def getLinkedSelection(self, masterIndex, masterSelection, slaveSelection):
    '''Filters the given list of entries and returns all selected entries'''
    masterEntry = masterSelection[masterIndex]
    linkValue = None
    if self.__key in masterEntry:
      linkValue = masterEntry[self.__key]

    resultSelection = list(dict(),)   
    for item in slaveSelection:
      if self.__key in item:
        if item[self.__key] == linkValue:
          resultSelection.append(item)
      else:
        if linkValue is None:
          #key does not exist, but selection value is None, therefore it is a match
          resultSelection.append(item)
        
          
    return resultSelection
  
    
class CaseLinker(KeyValueLinker):
  '''
      Links data on the basis of the artefactProps.CASE entry 
      usually the patient information is stored in case.
  '''
  def __init__(self):
    KeyValueLinker.__init__(self, artefactProps.CASE)

    

class TimePointLinker(KeyValueLinker):
  '''
      Links data on the basis of the artefactProps.TIMEPOINT entry 
      usually the patient information is stored in case.
  '''
  def __init__(self):
    KeyValueLinker.__init__(self, artefactProps.TIMEPOINT)