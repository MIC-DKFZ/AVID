__author__ = 'hentsch'

import sys
import os

import avid.common.workflow as workflow
from avid.selectors import ActionTagSelector
from avid.selectors import FormatSelector
from avid.selectors import CaseInstanceSelector
from avid.actions.mapR import mapRBatchAction as mapR
from avid.common.AVIDUrlLocater import getAVIDProjectRootPath
from avid.actions.regVarTool import RegVarToolBatchAction as regVar
from avid.actions.doseAcc import DoseAccBatchAction as doseAcc
from avid.actions.doseStats import DoseStatBatchAction as doseTool
from avid.actions.doseStatsCollector import DoseStatsCollectorBatchAction as doseStatsCollector

__this__ = sys.modules[__name__]

#regVarTemplatePath = os.path.join(getAVIDProjectRootPath(), "templates", "Gauss_trans.reg.var.xml")

NR_VARIATIONS=2
#ALGORITHMDLL = "D:/dev/AVIDPyWorkflow/rework_ng/Utilities/RegVarTool/mdra-0-12_RegVariationRandomGaussianEuler.dll"
ALGORITHMDLL = "D:/dev/AVIDPyWorkflow/rework_ng/Utilities/RegVarTool/mdra-0-12_RegVariationKernelRandomGaussianTPS.dll"
PARAMETERS = {"Mean" : "0.0", "StandardDeviation" : "1.0", "GridSize" : "2"}
REFERENCE_IMAGE = "D:/data/Sarkom Daten anonymized and cleaned/0001663996_SarkomPatient2/0001663996_SarkomPatient2_000__F01_stx.mhd"

with workflow.initSession_byCLIargs(name = "variationSession", expandPaths = True, autoSave = True) as session:
  regVar(ActionTagSelector("RegTool")+FormatSelector("MatchPoint"), NR_VARIATIONS, ALGORITHMDLL, PARAMETERS, REFERENCE_IMAGE, actionTag="RegVarTool", regVarToolExe = os.path.join("RegVarTool","RegVarTool.exe"), alwaysDo=False).do()

  for iteration in range(0,NR_VARIATIONS):
    mapR(ActionTagSelector("CCT"), ActionTagSelector("RegVarTool")+CaseInstanceSelector(iteration), templateSelector=ActionTagSelector("BPLCT"), outputExt = "nrrd", actionTag = "Mapped", alwaysDo=False).do()
  #  doseAcc(ActionTagSelector("Mapped")+CaseInstanceSelector(iteration), actionTag="DoseAcc", alwaysDo=False).do()

  #doseTool(ActionTagSelector("DoseAcc"),ActionTagSelector("struct"),['RUECKENMARK'], actionTag = "DoseTool", alwaysDo=False).do()
  #doseStatsCollector(ActionTagSelector("DoseTool"),['maximum'], actionTag = "DoseStatsCollector", alwaysDo=False).do()

