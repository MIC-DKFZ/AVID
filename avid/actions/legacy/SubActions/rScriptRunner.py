import subprocess
import avid.common.flatFileDictEntries as FFDE

def do(workflow, selector, RScriptExe):
  """
      Performs Execution of an R Script file
      Adds the config files generated in the inData container.
      Adds the result files to the inData container.
  """
  rFileList = selector.getFilteredContainer(workflow.artefacts)
  for rFile in rFileList:
    subprocess.call([RScriptExe, rFile[FFDE.URL]])
