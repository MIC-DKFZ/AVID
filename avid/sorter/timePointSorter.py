from avid.sorter import BaseSorter

import avid.common.artefact.defaultProps as artefactProps

class TimePointSorter(BaseSorter):
  '''Special version that enforces that time point is sorted as numeric.'''
  def __init__(self, reverse = False):
    self._reverse = reverse
        
  def sortSelection(self, selection):
    sortedSel = sorted(selection, key=lambda k: float(k[artefactProps.TIMEPOINT]), reverse = self._reverse)  
    return sortedSel