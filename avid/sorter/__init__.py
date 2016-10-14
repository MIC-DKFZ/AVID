class BaseSorter(object):
  '''base clase for functors used to sort a artefact list by certain criterias
  and pass back the sorted list.
  The default implementation does not touch the selection at all.'''
  def __init__(self):
    pass
  
  def sortSelection(self, selection):
    '''
    does nothing
    '''
    return selection
  
  
from keyValueSorter import KeyValueSorter
from timePointSorter import TimePointSorter