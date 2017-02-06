import os

from avid.common.flatFileEntryGenerator import FlatFileEntryGenerator
import avid.common.flatFileDictEntries as FFDE
import avid.common.templateFileCustomizer as templateFileCustomizer
from avid.common.osChecker import checkAndCreateDir
from avid.selectors.multiKeyValueSelector import MultiKeyValueSelector

CASE_INSTANCE    = str()
R_FILENAME = str()
ACTION_TAG    = str()
CASE_INSTANCE = str()

def do(workflow, doseStatAggregatedSelector, doseStatAggregatedCompareSelector, doseStatAggregatedSelectorBaseline, RTemplateFile, title, xAxisName, yAxisName, actionTag, caseInstance):
    """based on an csv file (header in first row + data in all other rows), a R file is generated based on a template file to visualize the data"""
    global ACTION_TAG, CASE_INSTANCE
    ACTION_TAG = actionTag

    CASE_INSTANCE = caseInstance
    """Create the directories"""
    outPath=os.path.join(workflow.outPath,actionTag,"config")
    xmlEntryOutPath=os.path.join(workflow.outPath,actionTag,"result")
    checkAndCreateDir(outPath)
    checkAndCreateDir(xmlEntryOutPath)

    RTemplateFile = os.path.join(workflow.templatePath, RTemplateFile)

    try:
      for i in range(0,workflow.numberOfPatients()):
        doseStatAggregatedSelector.updateKeyValueDict({FFDE.CASE:str(i)})
        doseStatsAggregatedList = doseStatAggregatedSelector.getFilteredContainer(workflow.artefacts)

        if doseStatAggregatedCompareSelector:
          doseStatAggregatedCompareSelector.updateKeyValueDict({FFDE.CASE:str(i)})
          doseStatsAggregatedCompareList = doseStatAggregatedCompareSelector.getFilteredContainer(workflow.artefacts)

        doseStatAggregatedSelectorBaseline.updateKeyValueDict({FFDE.CASE:str(i)})
        doseStatsAggregatedBaselineList = doseStatAggregatedSelectorBaseline.getFilteredContainer(workflow.artefacts)
        if doseStatsAggregatedBaselineList.__len__() != 1:
          raise
        cctSelector = MultiKeyValueSelector(workflow,{FFDE.CASE:str(i), FFDE.TYPE:"CCT"})
        cctList = cctSelector.getFilteredContainer(workflow.artefacts)
        fractions = _getFractions(cctList)
        maxFractions = _getMax(fractions)
        for element in doseStatsAggregatedList:
          if doseStatAggregatedCompareSelector:
            _writeRDiagramFileFromTemplate(outPath, element[FFDE.URL], doseStatsAggregatedCompareList[0][FFDE.URL], doseStatsAggregatedBaselineList[0][FFDE.URL], RTemplateFile, title, xAxisName, yAxisName)
          else:
            _writeRDiagramFileFromTemplate(outPath, element[FFDE.URL], None, doseStatsAggregatedBaselineList[0][FFDE.URL], RTemplateFile, title, xAxisName, yAxisName)
          absolutePngFilename = os.path.join(xmlEntryOutPath, CASE_INSTANCE + ".png")
          _addToInData(workflow, i, R_FILENAME, absolutePngFilename, maxFractions)
    except:
      raise


def _getFractions(list):
  return [int(element[FFDE.TIMEPOINT]) for element in list]

def _getMax(list):
  return max(list)

def _writeRDiagramFileFromTemplate(outPath, csvDataFile, csvCompareFile, csvBaselineFile, RTemplateFile, title, xAxisName, yAxisName):
  """load the .R template file and insert the missing values"""
  global R_FILENAME
  relativePngFilename = "../result/"+CASE_INSTANCE + ".png"
  workingDirectory = outPath.replace("\\", "/")
  csvDataFilename= csvDataFile.replace("\\", "/")
  csvBaselineFilename= csvBaselineFile.replace("\\", "/")
  if csvCompareFile:
    csvCompareFilename= csvCompareFile.replace("\\", "/")
  else:
    csvCompareFilename = ""

  R_FILENAME = os.path.join(outPath, CASE_INSTANCE+".R")

  replacingDict = {"@WORKING_DIRECTORY@" : workingDirectory, "@CSVDATA_FILE@" : csvDataFilename, "@CSVBASELINE_FILE@" : csvBaselineFilename, "@CSVADDITIONALDATA_FILE@" : csvCompareFilename,  "@PNG_FILE@": relativePngFilename, "@TITLE_NAME@" : title, "@XAXIS_NAME@":xAxisName, "@YAXIS_NAME@" : yAxisName }
  templateFileCustomizer.writeFileCustomized(RTemplateFile, R_FILENAME, replacingDict)


def _addToInData(workflow, case, rFilename, absolutePngFilename, nFractions):
  FFEGobj = FlatFileEntryGenerator()
  workflow.artefacts = FFEGobj.addRConfigToContainer(workflow.artefacts, str(case), str(nFractions), CASE_INSTANCE, str(rFilename),\
                                                                 ACTION_TAG)
  #technically, the PNG file is not yet generated here, but it is much more complicated to add the file to the workflow in rScriptRunner
  workflow.artefacts = FFEGobj.addPNGResultToContainer(workflow.artefacts, str(case), str(nFractions), CASE_INSTANCE, str(absolutePngFilename),\
                                                                 ACTION_TAG)
