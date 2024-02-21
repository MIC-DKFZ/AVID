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

from .artefact import defaultProps as artefactProps

def getNumberOfPatients(container):
  '''
     determines the number of patients
     Input is the flat file container of the workflow - list(dict()
  '''
  return len(getPatientsList(container))
    
def getPatientsList(container):
  ''' extracts all patient number entries of a workflow flat file container '''
  patientNumberList = list()
  for element in container:
    if int(element[artefactProps.CASE]) not in patientNumberList:
      patientNumberList += int(element[artefactProps.CASE]),
  return patientNumberList

