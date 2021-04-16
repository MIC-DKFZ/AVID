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

from avid.selectors import SelectorBase
import avid.common.artefact.defaultProps as artefactProps
from avid.common.artefact import getArtefactProperty

class ValiditySelector(SelectorBase):
  ''' Convenience selector to select only artefacts that are not invalid.'''
  def __init__(self, negate=False):
    ''' init '''
    super().__init__()
    self._negate = negate
    
  def getSelection(self, workflowData):
    '''Filters the given list of entries and returns all selected entries'''
    outList = list(dict(),)
    
    for entry in workflowData:
      value = getArtefactProperty(entry, artefactProps.INVALID)
      
      if (value is not True and not self._negate) or (value is True and self._negate):
        #value may also be None and should be seen as valid.
        outList.append(entry)
    return outList