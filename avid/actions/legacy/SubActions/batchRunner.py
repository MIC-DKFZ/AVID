import avid.common.execute as executer

from avid.common.actionToken import ACTION_LOG_LEVEL, ActionToken, boolToSuccess, logActionResult
 
import os

import avid.common.flatFileDictEntries as FFDE


def do(workflow,selector, patientNo = None):
    """Executes the batch files passed with the selector"""
    if patientNo != None:
      selector.updateKeyValueDict({FFDE.CASE:str(patientNo)})
    executeList = selector.getFilteredContainer(workflow.inData)
    for element in executeList:
      batFile = os.path.split(element[FFDE.URL])
      executer.execute(workflow, batFile[0], batFile[1])

     

