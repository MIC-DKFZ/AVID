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

import artefact.defaultProps as artefactProps

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

