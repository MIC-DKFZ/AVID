import os
import itertools

from avid.common.osChecker import checkAndCreateDir
from avid.common import templateFileCustomizer
import avid.common.flatFileDictEntries as FFDE
from avid.common.flatFileEntryGenerator import FlatFileEntryGenerator

ACTION_TAG    = str()
R_FILENAME = str()


def do(workflow, DVHDoseSelector, DVHVolumeSelector, RTemplateFile, title, xAxisName, yAxisName, actionTag):
    """based on an csv file (header in first file + data in second file), a R file is generated based on a template file to visualize the data"""
    global ACTION_TAG
    ACTION_TAG = actionTag
    """Create the directories"""
    outPath=os.path.join(workflow.outPath,actionTag,"config")
    xmlEntryOutPath=os.path.join(workflow.outPath,actionTag,"result")
    checkAndCreateDir(outPath)
    checkAndCreateDir(xmlEntryOutPath)

    RTemplateFile = os.path.join(workflow.templatePath, RTemplateFile)
    for i in range(0,workflow.numberOfPatients()):
      DVHDoseSelector.updateKeyValueDict({FFDE.CASE:str(i)})
      DVHVolumeSelector.updateKeyValueDict({FFDE.CASE:str(i)})
      DVHDoseAggregatedList = DVHDoseSelector.getFilteredContainer(workflow.artefacts)
      DVHVolumeAggregatedList = DVHVolumeSelector.getFilteredContainer(workflow.artefacts)
      for elementDose, elementVolume in itertools.izip(DVHDoseAggregatedList, DVHVolumeAggregatedList):
        csvFilename = os.path.basename(elementDose[FFDE.URL])
        iteration = int(os.path.splitext(csvFilename)[0].split("-")[1])
        #adjustment for transformation zero-based to one-based index ()
        iteration+=1
        relativePngFilename = "../result/" + "DVH-" + str(iteration) + ".png"
        _writeRDiagramFileFromTemplate(outPath, elementVolume[FFDE.URL], elementDose[FFDE.URL], RTemplateFile, title+str(iteration), xAxisName, yAxisName, relativePngFilename)
        absolutePngFilename = os.path.join(xmlEntryOutPath, "DVH-" + str(iteration) + ".png")
        _addToInData(workflow, i, elementDose[FFDE.TIMEPOINT], R_FILENAME, absolutePngFilename)

def _writeRDiagramFileFromTemplate(outPath, csvDataFile, csvHeaderFile, RTemplateFile, title, xAxisName, yAxisName, relativePngFilename):
  global R_FILENAME
  csvDataFileWithoutEnding =os.path.splitext(os.path.basename(csvDataFile))
  rRelativeFilename = csvDataFileWithoutEnding[0]+".r"
  rRelativeFilename = rRelativeFilename.replace("_Volume","")
  R_FILENAME = os.path.join(outPath, rRelativeFilename)
  workingDirectory = outPath.replace("\\", "/")
  csvDataFilename= csvDataFile.replace("\\", "/")
  csvHeaderFilename= csvHeaderFile.replace("\\", "/")

  replacingDict = {"@WORKING_DIRECTORY@" : workingDirectory, "@CSV_HEADER_FILE@" : csvHeaderFilename, "@CSV_DATA_FILE@" : csvDataFilename, "@TITLE_NAME@":title, "@XAXIS_NAME@":xAxisName, "@YAXIS_NAME@" : yAxisName, "@PNG_FILE@": "../result/"+relativePngFilename}
  templateFileCustomizer.writeFileCustomized(RTemplateFile, R_FILENAME, replacingDict)

def _addToInData(workflow, case, fraction, rFilename, absolutePngFilename):
  FFEGobj = FlatFileEntryGenerator()
  workflow.artefacts = FFEGobj.addRConfigToContainer(workflow.artefacts, str(case), str(fraction), "", str(rFilename),\
                                                                 ACTION_TAG)
  #technically, the PNG file is not yet generated here, but it is much more complicated to add the file to the workflow in rScriptRunner
  workflow.artefacts = FFEGobj.addPNGResultToContainer(workflow.artefacts, str(case), str(fraction), "", str(absolutePngFilename),\
                                                                 ACTION_TAG)