__author__ = 'hentsch'

import sys
import os
import argparse

import avid.common.workflow as workflow
import avid.common.artefact.defaultProps as artefactProps
import avid.common.demultiplexer as demux
from avid.selectors import ActionTagSelector
from avid.selectors import FormatSelector
from avid.selectors import TypeSelector
from avid.actions.regTool import regToolBatchAction as regTool
from avid.actions.mapR import mapRBatchAction as mapR
from avid.actions.pdc import pdcBatchAction as pdc
from avid.common.AVIDUrlLocater import getAVIDRootPath
from avid.actions.doseAcc import DoseAccBatchAction as doseAcc
from avid.actions.doseStats import DoseStatBatchAction as doseTool
from avid.actions.doseStatsCollector import DoseStatsCollectorBatchAction as doseStatsCollector
from avid.selectors.validitySelector import ValiditySelector

__this__ = sys.modules[__name__]

parser = argparse.ArgumentParser()
parser.add_argument('--style', choices=['externPC', 'externDose', 'externReg'])
cliargs, unkown = parser.parse_known_args()

execStyle = None
if cliargs.style is not None:
  execStyle = cliargs.style
  
transRegTemplate = os.path.join(getAVIDRootPath(), "python", "templates", "DIPP_translation_default.reg.xml")
rigidRegTemplate = os.path.join(getAVIDRootPath(), "python", "templates", "DIPP_rigid_default.reg.xml")
pdcTemplatePath = os.path.join(getAVIDRootPath(), "python", "templates", "PDC_DICOM_template.bat")

with workflow.initSession_byCLIargs(expandPaths = True, autoSave = True) as session:
  if execStyle is None: #do everything including the registration
    regTool(ActionTagSelector("PlCT"), ActionTagSelector("Control"), transRegTemplate, targetIsReference=False, actionTag = "PositionCorrection").do()
    mapR(ActionTagSelector("Control"), registrationSelector = ActionTagSelector("PositionCorrection"),  templateSelector=ActionTagSelector("PlCT"), outputExt = "dcm", actionTag = "Control_PC").do()
    
  if execStyle is None or execStyle == "externPC":
    pdc(ActionTagSelector("Control_PC"), ActionTagSelector("Plan"), ActionTagSelector("PlStruct"), executionBat= pdcTemplatePath, actionTag= "ControlDose").do()

  if execStyle is None or execStyle == "externPC" or execStyle == "externDose":
    regTool(ActionTagSelector("PlCT"), ActionTagSelector("Control_PC"), rigidRegTemplate, targetIsReference=False, actionTag = "ControlReg").do()
    doseAcc(ActionTagSelector("ControlDose")+FormatSelector(artefactProps.FORMAT_VALUE_ITK),\
            registrationSelector = ActionTagSelector("ControlReg"),\
            planSelector=ActionTagSelector("Plan"), actionTag="AccDose").do()
  else: #we have execStyle "externReg"
    doseAcc(ActionTagSelector("ControlDoseReg")+FormatSelector(artefactProps.FORMAT_VALUE_ITK),\
            planSelector=ActionTagSelector("Plan"), actionTag="AccDose").do()
  
  #resample work arround is needed because of a bug in the old voxelizer of dosetool.
  #can be removed when the new boost based implementation is in the master
  mapR(ActionTagSelector("PlDose"), templateSelector=ActionTagSelector("PlCT"), actionTag = "PlDose_Resampled").do()
  doseTool(ActionTagSelector("PlDose_Resampled"), ActionTagSelector("PlStruct"), session.definedStructures, actionTag = "DoseStats_Planned").do()

  #resample work arround is needed because of a bug in the old voxelizer of dosetool.
  #can be removed when the new boost based implementation is in the master
  mapR(ActionTagSelector("AccDose"), templateSelector=ActionTagSelector("PlCT"), actionTag = "AccDose_Resampled").do()
  doseTool(ActionTagSelector("AccDose_Resampled"),ActionTagSelector("PlStruct"), session.definedStructures, actionTag = "DoseStats_Acc").do()

  structSelectorDict = demux.getSelectors(artefactProps.OBJECTIVE, ActionTagSelector("DoseStats_Acc")+ValiditySelector()+TypeSelector(artefactProps.TYPE_VALUE_RESULT))

  for struct in structSelectorDict:
    doseStatsCollector(ActionTagSelector("DoseStats_Acc")+structSelectorDict[struct],['maximum', 'minimum', 'mean'], actionTag = "DoseStatsColl_Acc", alwaysDo = True).do()
