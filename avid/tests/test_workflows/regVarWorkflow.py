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
from avid.actions.regVarTool import RegVarToolBatchAction as regVar
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
pdcExe = os.path.join(getAVIDProjectRootPath(), "Utilities", "pdc++", "General", "bin", "PDC.exe" )
RSCRIPTEXE = "C:/Program Files/R/R-3.1.0/bin/Rscript.exe"

parser = argparse.ArgumentParser()
parser.add_argument('--variationParameters', nargs="*", default=[0.0, 1.0])
parser.add_argument('--nVariations', type=int, default=10)
cliargs, unknown = parser.parse_known_args()


if cliargs.nVariations is not None:
    nVariations = cliargs.nVariations
if cliargs.variationParameters is not None:
    variationParameters = cliargs.variationParameters

lastFraction = 25
alpha = 0.1
beta = 0.0333

if variationParameters.__len__() is not 2:
  raise

with workflow.initSession_byCLIargs(expandPaths=True, autoSave=True) as session:
  mapR(inputSelector=ActionTagSelector("CCT"), templateSelector=ActionTagSelector("BPLCT"), outputExt="ctx.gz", actionTag="MapCT").do()
  pdc(imageSelector=ActionTagSelector("MapCT"), planSelector=ActionTagSelector("plan"), structSelector=ActionTagSelector("struct"), executionBat=pdcTemplatePath,
      actionTag="DoseCalc", pdcExe=pdcExe).do()
  regVar(regs=ActionTagSelector("RegTool")+FormatSelector("MatchPoint"), variationCount=nVariations, templateSelector=regVarTemplatePath, paramters=variationParameters,
         actionTag="RegVarTool").do()

  for iteration in range(0, nVariations):
    doseAcc(doseSelector=ActionTagSelector("DoseCalc")+FormatSelector(artefactProps.FORMAT_VALUE_VIRTUOS),
            registrationSelector=ActionTagSelector("RegVarTool")+CaseInstanceSelector(iteration), planSelector=ActionTagSelector("plan"), actionTag="DoseAcc").do()

  doseAcc(doseSelector=ActionTagSelector("DoseCalc")+FormatSelector(artefactProps.FORMAT_VALUE_VIRTUOS),
          registrationSelector=ActionTagSelector("RegTool")+FormatSelector("MatchPoint"), planSelector=ActionTagSelector("plan"), actionTag="DoseAccOriginal").do()

  bioModelCalc(inputSelector=ActionTagSelector("DoseAcc")+TimepointSelector(lastFraction), modelParameters=[alpha, beta/lastFraction], modelName="LQ",
               actionTag="BioModelVariedDose").do()
  bioModelCalc(inputSelector=ActionTagSelector("dose")+FormatSelector(artefactProps.FORMAT_VALUE_VIRTUOS), modelParameters=[alpha, beta/lastFraction],
               modelName="LQ", actionTag="BioModelPlannedDose").do()
  bioModelCalc(inputSelector=ActionTagSelector("DoseAccOriginal")+TimepointSelector(lastFraction), modelParameters=[alpha, beta/lastFraction], modelName="LQ",
               actionTag="BioModelActualDose").do()

  doseTool(inputSelector=ActionTagSelector("dose"), structSetSelector=ActionTagSelector("struct"), structNames=session.structureDefinitions, actionTag="DoseToolPlanned").do()
  doseTool(inputSelector=ActionTagSelector("DoseAcc"), structSetSelector=ActionTagSelector("struct"), structNames=session.structureDefinitions, actionTag="DoseTool").do()
  doseTool(inputSelector=ActionTagSelector("DoseAccOriginal"), structSetSelector=ActionTagSelector("struct"), structNames=session.structureDefinitions,
           actionTag="DoseToolActual").do()

  doseStatsWithInterpolationCollector(inputSelector=ActionTagSelector("DoseToolPlanned"), planSelector=ActionTagSelector("plan"), selectedStats=['maximum', 'minimum', 'mean'],
                                      actionTag="DoseStatsPlannedCollector").do()
  doseStatsCollector(inputSelector=ActionTagSelector("DoseTool"), selectedStats=['maximum', 'minimum', 'mean'], actionTag="DoseStatsCollector").do()
  doseStatsCollector(inputSelector=ActionTagSelector("DoseToolActual"), selectedStats=['maximum', 'minimum', 'mean'], actionTag="DoseStatsActualCollector").do()

  doseProcessVisualizer(doseStatVariationsSelector=ActionTagSelector("DoseStatsCollector")+DoseStatSelector("maximum"),
                        doseStatBaselineSelector=ActionTagSelector("DoseStatsPlannedCollector")+DoseStatSelector("maximum"),
                        doseStatAdditionalSelector=ActionTagSelector("DoseStatsActualCollector")+DoseStatSelector("maximum"),
                        rTemplateFile=os.path.join(templatePath, "diagramCSVSource.R"), diagramTitle="Uncertainty Max Dose", xAxisName="Fractions",
                        yAxisName="Dose (Gy)", actionTag="DoseProcessVisualizer", rScriptExe=RSCRIPTEXE).do()
  doseProcessVisualizer(doseStatVariationsSelector=ActionTagSelector("DoseStatsCollector")+DoseStatSelector("maximum"),
                        doseStatBaselineSelector=ActionTagSelector("DoseStatsPlannedCollector")+DoseStatSelector("maximum"),
                        doseStatAdditionalSelector=ActionTagSelector("DoseStatsActualCollector")+DoseStatSelector("maximum"),
                        rTemplateFile=os.path.join(templatePath, "deltaDiagramWithQuantilAndAdditionalDataCSVSource.R"), diagramTitle="Uncertainty Delta-View Max Dose",
                        xAxisName="Fractions", yAxisName="Delta Dose (Gy)", actionTag="DoseProcessVisualizer", rScriptExe=RSCRIPTEXE).do()
  doseProcessVisualizer(doseStatVariationsSelector=ActionTagSelector("DoseStatsCollector")+DoseStatSelector("maximum"),
                        doseStatBaselineSelector=ActionTagSelector("DoseStatsPlannedCollector")+DoseStatSelector("maximum"),
                        doseStatAdditionalSelector=ActionTagSelector("DoseStatsActualCollector")+DoseStatSelector("maximum"),
                        rTemplateFile=os.path.join(templatePath, "boxplotWithAdditionalDataCSVSource.R"), diagramTitle="Uncertainty Max Dose last fraction",
                        xAxisName="", yAxisName="Delta Dose (Gy)", actionTag="DoseProcessVisualizer", rScriptExe=RSCRIPTEXE).do()

  cleanWorkflow(ActionTagSelector("DoseAcc")).do()