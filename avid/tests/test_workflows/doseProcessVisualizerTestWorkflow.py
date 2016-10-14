__author__ = 'hentsch'

import sys, os

import avid.common.workflow as workflow
from avid.selectors.keyValueSelector import ActionTagSelector
from avid.selectors.keyValueSelector import DoseStatSelector
from avid.actions.doseProcessVisualizer import doseProcessVisualizerBatchAction as doseProcessVisualizer
from avid.common.AVIDUrlLocater import getAVIDRootPath

__this__ = sys.modules[__name__]

RSCRIPTEXE = "C:/Program Files/R/R-3.1.0/bin/Rscript.exe"
templatePath = os.path.join(getAVIDRootPath(), "python", "templates")

with workflow.initSession_byCLIargs(expandPaths = True, autoSave = True) as session:

  doseProcessVisualizer(ActionTagSelector("DoseStatsCollector")+DoseStatSelector("maximum"), ActionTagSelector("DoseStatsPlannedCollector")+DoseStatSelector("maximum"), ActionTagSelector("DoseStatsActualCollector")+DoseStatSelector("maximum"), os.path.join(templatePath, "diagramCSVSource.R"), "Uncertainty Max Dose", "Fractions", "Dose (Gy)", actionTag = "DoseProcessVisualizer", rScriptExe=RSCRIPTEXE).do()
  doseProcessVisualizer(ActionTagSelector("DoseStatsCollector")+DoseStatSelector("maximum"), ActionTagSelector("DoseStatsPlannedCollector")+DoseStatSelector("maximum"), ActionTagSelector("DoseStatsActualCollector")+DoseStatSelector("maximum"), os.path.join(templatePath, "deltaDiagramWithQuantilAndAdditionalDataCSVSource.R"), "Uncertainty Delta-View Max Dose", "Fractions", "Delta Dose (Gy)", actionTag = "DoseProcessVisualizer", rScriptExe=RSCRIPTEXE).do()
  doseProcessVisualizer(ActionTagSelector("DoseStatsCollector")+DoseStatSelector("maximum"), ActionTagSelector("DoseStatsPlannedCollector")+DoseStatSelector("maximum"), ActionTagSelector("DoseStatsActualCollector")+DoseStatSelector("maximum"), os.path.join(templatePath, "boxplotWithAdditionalDataCSVSource.R"), "Uncertainty Max Dose last fraction", "", "Delta Dose (Gy)", actionTag = "DoseProcessVisualizer", rScriptExe=RSCRIPTEXE).do()
