''' 
  This module offers methods for correct generation ore adding of artefact entries
  tis responsible to add new dict entries in the flat file data container 
'''

import defaultProps
from avid.common.artefact import Artefact

def generateArtefactEntry(case, caseInstance, timePoint, actionTag, artefactType, artefactFormat, url = None, objective= None, invalid = False, **additionalProps):
  ''' 
      This is a generic method to generate an arbitrary artefact entry. 
      dict (**kwargs)  can be used to pass additional infos for the dict entry
      @param case Case ID for the artefact (e.g. Patient ID). May be set to None
      to indicate that it is a general artefact (not case specific).
      @param caseInstance ID of a case instance. May be set to None to indicate
      that the artefact has/is no variation
      @param timePoint Timepoint the artefact is corelated with. Should be an
      ordinal type (e.g. int or str)
      @param actionTag Tag of the action that generates/generated the artefact.
      @param artefactType Type of the artefact (e.g. "result", "config", "misc")
      @param artefactFormat Formate the artefact is stored as
      @param url Location where the artefact is stored
      @param objective the objective of the artefact (may be set to None)
      @param invalid Indicates if the artefact is valid (e.g. correctly stored)
      @param **additionalProps additional properties you want to add to the artefact entry     
  ''' 
  artefact = Artefact()
  
  artefact[defaultProps.CASE] = case
  artefact[defaultProps.CASEINSTANCE] = caseInstance 
  artefact[defaultProps.TIMEPOINT] = timePoint 
  artefact[defaultProps.ACTIONTAG] = actionTag 
  artefact[defaultProps.TYPE] = artefactType 
  artefact[defaultProps.FORMAT] = artefactFormat
  artefact[defaultProps.URL] = url 
  artefact[defaultProps.OBJECTIVE] = objective 
  artefact[defaultProps.INVALID] = invalid
    
  for key in (additionalProps):
    artefact[key] = additionalProps[key]
  
  return artefact 
