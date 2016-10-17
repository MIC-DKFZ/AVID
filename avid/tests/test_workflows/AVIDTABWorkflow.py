__author__ = 'hentsch'

import sys
import os

import avid.common.workflow as workflow
import avid.common.artefact.defaultProps as artefactProps
import avid.common.demultiplexer as demux
from avid.selectors import ActionTagSelector
from avid.selectors import FormatSelector
from avid.actions.regTool import regToolBatchAction as regTool
from avid.actions.mapR import mapRBatchAction as mapR
from avid.actions.pdc import pdcBatchAction as pdc
from avid.common.AVIDUrlLocater import getAVIDProjectRootPath
from avid.actions.doseAcc import DoseAccBatchAction as doseAcc
from avid.actions.doseStats import DoseStatBatchAction as doseTool
from avid.actions.doseStatsCollector import DoseStatsCollectorBatchAction as doseStatsCollector
from avid.selectors.validitySelector import ValiditySelector

__this__ = sys.modules[__name__]

transRegTemplate = os.path.join(getAVIDProjectRootPath(), "templates", "DIPP_translation_default.reg.xml")
rigidRegTemplate = os.path.join(getAVIDProjectRootPath(), "templates", "DIPP_rigid_default.reg.xml")
pdcTemplatePath = os.path.join(getAVIDProjectRootPath(), "templates", "PDC_DICOM_template.bat")

doRegistration = False
doPDC = False
doDoseAccResampling = False

with workflow.initSession_byCLIargs(expandPaths = True, autoSave = True) as session:
  if doRegistration:
    regTool(ActionTagSelector("PlCT"), ActionTagSelector("Control"), transRegTemplate, targetIsReference=False, actionTag = "PositionCorrection", alwaysDo=True).do()
    mapR(ActionTagSelector("Control"), registrationSelector = ActionTagSelector("PositionCorrection"),  templateSelector=ActionTagSelector("PlCT"), actionTag = "Control_PC").do()
    if doPDC:
      pdc(ActionTagSelector("Control_PC"), ActionTagSelector("Plan"), ActionTagSelector("PlStruct"), executionBat= pdcTemplatePath, actionTag= "ControlDose").do()
    regTool(ActionTagSelector("PlCT"), ActionTagSelector("Control_PC"), rigidRegTemplate, targetIsReference=False, actionTag = "ControlReg").do()
    doseAcc(ActionTagSelector("ControlDose")+FormatSelector(artefactProps.FORMAT_VALUE_ITK),\
            registrationSelector = ActionTagSelector("ControlReg"),\
            planSelector=ActionTagSelector("Plan"), actionTag="AccDose").do()
  else:
    doseAcc(ActionTagSelector("ControlDoseReg")+FormatSelector(artefactProps.FORMAT_VALUE_ITK),\
            planSelector=ActionTagSelector("Plan"), actionTag="AccDose").do()

  mapR(ActionTagSelector("PlDose"), templateSelector=ActionTagSelector("PlCT"), actionTag = "PlDose_Resampled").do()
  doseTool(ActionTagSelector("PlDose_Resampled"), ActionTagSelector("PlStruct"), session.definedStructures, actionTag = "DoseStats_Planned").do()

  if doDoseAccResampling:
    mapR(ActionTagSelector("AccDose"), templateSelector=ActionTagSelector("PlCT"), actionTag = "AccDose_Resampled").do()
    doseTool(ActionTagSelector("AccDose_Resampled"),ActionTagSelector("PlStruct"), session.definedStructures, actionTag = "DoseStats_Acc").do()
  else:
    doseTool(ActionTagSelector("AccDose"), ActionTagSelector("PlStruct"), session.definedStructures, actionTag = "DoseStats_Acc").do()

  structSelectorDict = demux.getSelectors(artefactProps.OBJECTIVE, ActionTagSelector("DoseStats_Acc")+ValiditySelector())

  for struct in structSelectorDict:
    doseStatsCollector(ActionTagSelector("DoseStats_Acc")+structSelectorDict[struct],['maximum', 'minimum', 'mean'], actionTag = "DoseStatsColl_Acc", alwaysDo = True).do()
