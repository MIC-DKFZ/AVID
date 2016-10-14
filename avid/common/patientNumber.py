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

