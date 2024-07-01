# SPDX-FileCopyrightText: 2024, German Cancer Research Center (DKFZ), Division of Medical Image Computing (MIC)
#
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# or find it in LICENSE.txt.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
  This module offers methods for correct generation ore adding of artefact entries
  tis responsible to add new dict entries in the flat file data container
"""

from . import defaultProps
from avid.common.artefact import Artefact

def generateArtefactEntry(case, caseInstance, timePoint, actionTag, artefactType, artefactFormat, url = None, objective= None, invalid = False, **additionalProps):
  '''
  REMARK: This is a deprecated verion. With less default and different order of arguments in signature.
  Use the new version generate_artefact_entry if possible.
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


def generate_artefact_entry(case, time_point, action_tag, artefact_type=defaultProps.TYPE_VALUE_RESULT,
                            case_instance=None, url=None, objective=None, invalid=False, **additional_props):
    """
        This is a generic method to generate an arbitrary artefact entry.
        dict (**kwargs)  can be used to pass additional infos for the dict entry
        @param case Case ID for the artefact (e.g. Patient ID). May be set to None
        to indicate that it is a general artefact (not case specific).
        @param case_instance ID of a case instance. May be set to None to indicate
        that the artefact has/is no variation
        @param time_point Timepoint the artefact is correlated with. Should be an
        ordinal type (e.g. int or str)
        @param action_tag Tag of the action that generates/generated the artefact.
        @param artefact_type Type of the artefact (e.g. "result", "config", "misc")
        @param url Location where the artefact is stored
        @param objective the objective of the artefact (may be set to None)
        @param invalid Indicates if the artefact is valid (e.g. correctly stored)
        @param **additional_props additional properties you want to add to the artefact entry
    """
    artefact = Artefact()

    artefact[defaultProps.CASE] = case
    artefact[defaultProps.CASEINSTANCE] = case_instance
    artefact[defaultProps.TIMEPOINT] = time_point
    artefact[defaultProps.ACTIONTAG] = action_tag
    artefact[defaultProps.TYPE] = artefact_type
    artefact[defaultProps.URL] = url
    artefact[defaultProps.OBJECTIVE] = objective
    artefact[defaultProps.INVALID] = invalid

    for key in additional_props:
      artefact[key] = additional_props[key]

    return artefact
