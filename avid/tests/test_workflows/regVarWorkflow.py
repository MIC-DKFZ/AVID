__author__ = 'hentsch'

import sys
import os
import argparse

import avid.common.workflow as workflow
import avid.common.artefact.defaultProps as artefactProps
from avid.selectors import ActionTagSelector
from avid.selectors import FormatSelector
from avid.selectors import CaseInstanceSelector
from avid.selectors import TimepointSelector
from avid.selectors import DoseStatSelector
from avid.actions.mapR import mapRBatchAction as mapR
from avid.actions.pdc import pdcBatchAction as pdc
from avid.actions.cleanWorkflow import cleanWorkflowBatchAction as cleanWorkflow
from avid.common.AVIDUrlLocater import getAVIDProjectRootPath
from avid.actions.regVarTool import RegVariationToolBatchAction as regVar
from avid.actions.doseAcc import DoseAccBatchAction as doseAcc
from avid.actions.doseStats import DoseStatBatchAction as doseTool
from avid.actions.doseStatsCollector import DoseStatsCollectorBatchAction as doseStatsCollector
from avid.actions.DoseStatsWithInterpolationCollector import DoseStatsWithInterpolationCollectorBatchAction as doseStatsWithInterpolationCollector
from avid.actions.doseProcessVisualizer import doseProcessVisualizerBatchAction as doseProcessVisualizer
from avid.actions.bioModelCalc import BioModelCalcBatchAction as bioModelCalc

__this__ = sys.modules[__name__]

templatePath = os.path.join(getAVIDProjectRootPath(), "templates")
pdcTemplatePath = os.path.join(getAVIDProjectRootPath(), "templates", "PDC_template.bat")
regVarTemplatePath = os.path.join(getAVIDProjectRootPath(), "templates", "Gauss_trans.reg.var.xml")
pdcExe = os.path.join(getAVIDProjectRootPath(),"Utilities","pdc++", "General", "bin", "PDC.exe" )
RSCRIPTEXE = "C:/Program Files/R/R-3.1.0/bin/Rscript.exe"

parser = argparse.ArgumentParser()
parser.add_argument('--variationParameters', nargs="*", default=[0.0, 1.0])
parser.add_argument('--nVariations', type=int, default=10)
cliargs, unknown = parser.parse_known_args()


if cliargs.nVariations is not None:
    nVariations = cliargs.nVariations
if cliargs.variationParameters is not None:
    variationParameters = cliargs.variationParameters

lastFraction = 25#
alpha = 0.1
beta = 0.0333

if variationParameters.__len__() is not 2:
  raise

with workflow.initSession_byCLIargs(expandPaths = True, autoSave = True) as session:
  mapR(ActionTagSelector("CCT"), templateSelector=ActionTagSelector("BPLCT"), outputExt = "ctx.gz", actionTag = "MapCT").do()
  pdc(ActionTagSelector("MapCT"), ActionTagSelector("plan"), ActionTagSelector("struct"), executionBat= pdcTemplatePath, actionTag= "DoseCalc", pdcExe=pdcExe).do()
  regVar(ActionTagSelector("RegTool")+FormatSelector("MatchPoint"), nVariations, regVarTemplatePath, variationParameters[0], variationParameters[1], actionTag="RegVarTool", regVariationToolExe = os.path.join("RegVariationTool","RegVariationTool.exe")).do()
#
  #for iteration in range(0,nVariations):
  #  doseAcc(ActionTagSelector("DoseCalc")+FormatSelector(artefactProps.FORMAT_VALUE_VIRTUOS),ActionTagSelector("RegVarTool")+CaseInstanceSelector(iteration),ActionTagSelector("plan"), actionTag="DoseAcc").do()
#
  #doseAcc(ActionTagSelector("DoseCalc")+FormatSelector(artefactProps.FORMAT_VALUE_VIRTUOS),ActionTagSelector("RegTool")+FormatSelector("MatchPoint"),ActionTagSelector("plan"), actionTag="DoseAccOriginal").do()
#
  #bioModelCalc(ActionTagSelector("DoseAcc")+TimepointSelector(lastFraction), modelParameters=[alpha, beta/lastFraction], modelName="LQ", actionTag = "BioModelVariedDose").do()
  #bioModelCalc(ActionTagSelector("dose")+FormatSelector(artefactProps.FORMAT_VALUE_VIRTUOS), modelParameters=[alpha, beta/lastFraction], modelName="LQ", actionTag = "BioModelPlannedDose").do()
  #bioModelCalc(ActionTagSelector("DoseAccOriginal")+TimepointSelector(lastFraction), modelParameters=[alpha, beta/lastFraction], modelName="LQ", actionTag = "BioModelActualDose").do()
#
  #doseTool(ActionTagSelector("dose"),ActionTagSelector("struct"),session.structureDefinitions, actionTag = "DoseToolPlanned").do()
  #doseTool(ActionTagSelector("DoseAcc"),ActionTagSelector("struct"),session.structureDefinitions, actionTag = "DoseTool").do()
  #doseTool(ActionTagSelector("DoseAccOriginal"),ActionTagSelector("struct"),session.structureDefinitions, actionTag = "DoseToolActual").do()
#
  doseStatsWithInterpolationCollector(ActionTagSelector("DoseToolPlanned"), ActionTagSelector("plan"), ['maximum', 'minimum', 'mean'], actionTag = "DoseStatsPlannedCollector").do()
  doseStatsCollector(ActionTagSelector("DoseTool"),['maximum', 'minimum', 'mean'], actionTag = "DoseStatsCollector").do()
  doseStatsCollector(ActionTagSelector("DoseToolActual"),['maximum', 'minimum', 'mean'], actionTag = "DoseStatsActualCollector").do()

  #doseProcessVisualizer(ActionTagSelector("DoseStatsCollector")+DoseStatSelector("maximum"), ActionTagSelector("DoseStatsPlannedCollector")+DoseStatSelector("maximum"), ActionTagSelector("DoseStatsActualCollector")+DoseStatSelector("maximum"), os.path.join(templatePath, "diagramCSVSource.R"), "Uncertainty Max Dose", "Fractions", "Dose (Gy)", actionTag = "DoseProcessVisualizer", rScriptExe=RSCRIPTEXE).do()
  #doseProcessVisualizer(ActionTagSelector("DoseStatsCollector")+DoseStatSelector("maximum"), ActionTagSelector("DoseStatsPlannedCollector")+DoseStatSelector("maximum"), ActionTagSelector("DoseStatsActualCollector")+DoseStatSelector("maximum"), os.path.join(templatePath, "deltaDiagramWithQuantilAndAdditionalDataCSVSource.R"), "Uncertainty Delta-View Max Dose", "Fractions", "Delta Dose (Gy)", actionTag = "DoseProcessVisualizer", rScriptExe=RSCRIPTEXE).do()
  #doseProcessVisualizer(ActionTagSelector("DoseStatsCollector")+DoseStatSelector("maximum"), ActionTagSelector("DoseStatsPlannedCollector")+DoseStatSelector("maximum"), ActionTagSelector("DoseStatsActualCollector")+DoseStatSelector("maximum"), os.path.join(templatePath, "boxplotWithAdditionalDataCSVSource.R"), "Uncertainty Max Dose last fraction", "", "Delta Dose (Gy)", actionTag = "DoseProcessVisualizer", rScriptExe=RSCRIPTEXE).do()

  #cleanWorkflow(ActionTagSelector("DoseAcc")).do()
