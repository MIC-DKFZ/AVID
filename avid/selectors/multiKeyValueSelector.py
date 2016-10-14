from avid.selectors import SelectorBase

class MultiKeyValueSelector(SelectorBase):
  '''
      extracts the entries of the working data, which has the specified key//value entries.
      e.g.
      key = "tag", value = "CCT"
      the selectors extracts all rows, which have a key tag, and the value is CCT.
  '''
  def __init__(self,selectionDict):
    ''' init '''
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
    outList = list(dict(),)
    try:
      for entry in container:
        if dictEntry in entry:
          if entry[dictEntry] == self.__selectionDict[dictEntry]:
            outList.append(entry)
        else:
          if self.__selectionDict[dictEntry] is None:
            outList.append(entry)
      return outList
    except KeyError:
      print ("A key (%s) was specified, which is not stored in the input data!",dictEntry)
      self.__workflow.getLogger().info("A key (%s) was specified, which is not stored in the input data!",dictEntry)  