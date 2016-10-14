__author__ = 'floca'

import sys
import os
import argparse
import ntpath

import avid.common.workflow as workflow
import avid.common.artefact.defaultProps as defaultProps
import avid.common.artefact
from avid.selectors import ActionTagSelector
from avid.selectors import KeyValueSelector
from avid.actions.mapR import mapRBatchAction as mapR
from avid.actions.regTool import regToolBatchAction as regTool
from avid.actions.doseMap import DoseMapBatchAction as doseMap
from avid.actions.doseStats import DoseStatBatchAction as doseStats
from avid.actions.doseStatsCollector import DoseStatsCollectorBatchAction as statsCollector
import avid.common.demultiplexer as demux

__this__ = sys.modules[__name__]

###############################################################################
# 1st pass command line parsing
###############################################################################
parser = argparse.ArgumentParser()
parser.add_argument('--algorithmPath')
cliargs, unknown = parser.parse_known_args()

if cliargs.algorithmPath is not None:
    algorithmPath = cliargs.algorithmPath

###############################################################################
# configure system to use method id as additional distinctive artefact property
###############################################################################
methodProperty = "method"
avid.common.artefact.similarityRelevantProperties = avid.common.artefact.similarityRelevantProperties + [methodProperty]

def _methodSpecificGenerateArtefactPath(workflow, workflowArtefact):
  """ Generates the path derived from the workflow informations and the
      properties of the artefact. This default style will generate the following
      path:
      [workflow.outputpath]+[workflow.name]+[artefact.actiontag]+[artefact.type]
      +[artefact.case]+[artefact.caseinstance]
      The case and caseinstance parts are skipped if the respective
      value is NONE. """
  artefactPath = os.path.join(workflow.rootPath, workflow.name, workflowArtefact[defaultProps.ACTIONTAG], workflowArtefact[defaultProps.TYPE])
  if workflowArtefact[defaultProps.CASE] is not None:
    artefactPath = os.path.join(artefactPath, str(workflowArtefact[defaultProps.CASE]))
  if workflowArtefact[defaultProps.CASEINSTANCE] is not None:
    artefactPath = os.path.join(artefactPath, str(workflowArtefact[defaultProps.CASEINSTANCE]))
  if methodProperty in workflowArtefact and workflowArtefact[methodProperty] is not None:
    artefactPath = os.path.join(artefactPath, str(workflowArtefact[methodProperty]))
    
  return artefactPath

avid.common.artefact.pathGenerationDelegate = _methodSpecificGenerateArtefactPath

###############################################################################
# get all algorithms under evaluation (AUE)
###############################################################################

aue = dict()

for aFile in os.listdir(algorithmPath):
    if aFile.endswith(".reg.xml"):
      aue[ntpath.basename(aFile)] = os.path.join(algorithmPath, aFile)

###############################################################################
# general setup selectors for a more readable script
###############################################################################
BPLCTSelector = ActionTagSelector("BPLCT")
ControlSelector = ActionTagSelector("Control")
PlanSelector = ActionTagSelector("Plan")
PlanDoseSelector = ActionTagSelector("PlanDose")
StructsSelector = ActionTagSelector("Structs")
ControlDoseSelector = ActionTagSelector("ControlDose")   
MappedDoseSelector = ActionTagSelector("MappedDose")   
RegSelector = ActionTagSelector("Registration")
DoseStatsMappedSelector = ActionTagSelector("DoseStats_Mapped")

###############################################################################
# the workflow itself
###############################################################################
with workflow.initSession_byCLIargs(expandPaths=True, autoSave=True) as session:
    
  for aueID in aue:
    #Registration and mapping must be done explicitly AUE specific. Reason additional action properties are currently only implicitly derived from the master artefacts.  
    AUESelector = KeyValueSelector(methodProperty, aueID) 
    regTool(BPLCTSelector, ControlSelector, aue[aueID], targetIsReference=False, actionTag="Registration", additionalActionProps={methodProperty: aueID}).do()
    mapR(ControlSelector, RegSelector+AUESelector, BPLCTSelector, actionTag="MappedControl", mapRExe=os.path.join("mapR4V", "mapR4V.exe"), additionalActionProps={methodProperty: aueID}).do()
    doseMap(ControlDoseSelector, RegSelector+AUESelector, PlanDoseSelector, actionTag="MappedDose", additionalActionProps={methodProperty: aueID}).do()
    
  #compute statistics
  doseStats(PlanDoseSelector, StructsSelector, session.definedStructures, actionTag="DoseStats_Planned").do()
  doseStats(MappedDoseSelector, StructsSelector, session.definedStructures, actionTag="DoseStats_Mapped").do()
  
  #collect everything into tables
  structSelectors = demux.getSelectors(defaultProps.OBJECTIVE, DoseStatsMappedSelector)
  for structID in structSelectors:
    statsCollector(DoseStatsMappedSelector+structSelectors[structID],['maximum', 'minimum', 'mean'], rowKey = defaultProps.CASE, columnKey = methodProperty, actionTag = "DoseStatsColl_Acc", alwaysDo = True).do()  
    