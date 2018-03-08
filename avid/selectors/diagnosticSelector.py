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
from avid.selectors import KeyValueSelector
from avid.selectors import SelectorBase
import avid.common.artefact.defaultProps as artefactProps
from avid.common.artefact import getArtefactProperty
from avid.selectors import ValiditySelector

def getInputArtefactIDs(workflowData):
  inputs = set()

  for entry in workflowData:
    value = getArtefactProperty(entry, artefactProps.INPUT_IDS)

    for ID in list(value.values()):
      inputs.add(ID)

  return list(inputs)

class IsInputSelector(SelectorBase):
  ''' Convenience selector to select only artefacts that are inputs of other artefacts in the given workflow data.'''
  def __init__(self):
    ''' init '''
    pass
    
  def getSelection(self, workflowData):
    '''Filters the given list of entries and returns all selected entries'''
    outList = list(dict(),)

    inputs = getInputArtefactIDs(workflowData)

    [outList.append(x) for x in workflowData if x[artefactProps.ID] in inputs]

    return outList


class IsPrimeInvalidSelector(SelectorBase):
  ''' Convenience selector to select only artefacts that are invalid but have none or valid input artefacts in the given workflow data.'''

  def __init__(self):
    ''' init '''
    pass

  def getSelection(self, workflowData):
    '''Filters the given list of entries and returns all selected entries'''

    valid_artefacts = ValiditySelector().getSelection(workflowData)

    valid_ids = [x[artefactProps.ID] for x in valid_artefacts if not x[artefactProps.INVALID]]

    outList = list(dict(),)
    for entry in workflowData:
      input_ids = getArtefactProperty(entry, artefactProps.INPUT_IDS)

      found = False
      if input_ids is not None and entry[artefactProps.INVALID]:
        found = True
        for ID in list(input_ids.values()):
          if not ID in valid_ids:
            found = False
      if found:
        outList.append(entry)

    return outList

class RootSelector(SelectorBase):
  ''' Convenience selector to select all artefacts that have no inputs.'''
  def __init__(self):
    ''' init '''
    pass

  def getSelection(self, workflowData):
    '''Filters the given list of entries and returns all selected entries'''

    outList = list(dict(),)
    for entry in workflowData:
      input_ids = getArtefactProperty(entry, artefactProps.INPUT_IDS)
      if input_ids is None or len(input_ids)==0:
        outList.append(entry)

    return outList