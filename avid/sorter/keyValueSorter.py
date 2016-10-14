from avid.sorter import BaseSorter

class KeyValueSorter(BaseSorter):
  '''Sorts the selection by the values of a passed property key.'''
  def __init__(self, key, reverse = False):
    self._key = key
    self._reverse = reverse
        
  def sortSelection(self, selection):
    sortedSel = sorted(selection, key=lambda k: k[self._key], reverse = self._reverse)  
    return sortedSel