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

from avid.linkers import InnerLinkerBase

import avid.common.artefact.defaultProps as artefactProps

class KeyValueLinker(InnerLinkerBase):
  '''
      Links data based on the value of a given key.
  '''
  def __init__(self, key, allowOnlyFullLinkage = True, performInternalLinkage=False):
    '''@param key The key of the artefacts that should be used to compare the values.
       For details of the other paramerter, see base class.
    '''
    InnerLinkerBase.__init__(self, allowOnlyFullLinkage=allowOnlyFullLinkage,
                             performInternalLinkage=performInternalLinkage)
    self._key = key

  def _findLinkedArtefactOptions(self, primaryArtefact, secondarySelection):
    linkValue = None
    if primaryArtefact is not None and self._key in primaryArtefact:
      linkValue = primaryArtefact[self._key]

    foundArtefacts = list()

    for secondaryArtefact in secondarySelection:

      if secondaryArtefact is not None and self._key in secondaryArtefact:
        if secondaryArtefact[self._key] == linkValue:
          foundArtefacts.append(secondaryArtefact)
      else:
        if linkValue is None:
          # key does not exist, but selection value is None, therefore it is a match
          foundArtefacts.append(secondaryArtefact)

    return foundArtefacts

    
class CaseLinker(KeyValueLinker):
  '''
      Links data on the basis of the artefactProps.CASE entry 
      usually the patient information is stored in case.
  '''
  def __init__(self, allowOnlyFullLinkage = True, performInternalLinkage=False):
    KeyValueLinker.__init__(self, artefactProps.CASE, allowOnlyFullLinkage=allowOnlyFullLinkage,
                            performInternalLinkage=performInternalLinkage)

    

class TimePointLinker(KeyValueLinker):
  '''
      Links data on the basis of the artefactProps.TIMEPOINT entry 
      usually the patient information is stored in case.
  '''
  def __init__(self, allowOnlyFullLinkage = True, performInternalLinkage=False):
    KeyValueLinker.__init__(self, artefactProps.TIMEPOINT, allowOnlyFullLinkage=allowOnlyFullLinkage,
                            performInternalLinkage=performInternalLinkage)