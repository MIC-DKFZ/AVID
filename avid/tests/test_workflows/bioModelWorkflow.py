__author__ = 'hentsch'

import sys
import os

import avid.common.workflow as workflow
import avid.common.artefact.defaultProps as artefactProps
from avid.selectors import ActionTagSelector
from avid.selectors import FormatSelector
from avid.selectors import TimepointSelector
from avid.actions.mapR import mapRBatchAction as mapR
from avid.actions.bioModelCalc import BioModelCalcBatchAction as bioModelCalc
from avid.actions.pdc import pdcBatchAction as pdc
from avid.common.AVIDUrlLocater import getAVIDRootPath
from avid.actions.doseAcc import DoseAccBatchAction as doseAcc
from avid.actions.doseStats import DoseStatBatchAction as doseTool
from avid.actions.doseMap import DoseMapBatchAction as doseMap

__this__ = sys.modules[__name__]

templatePath = os.path.join(getAVIDRootPath(), "python", "templates")
pdcTemplatePath = os.path.join(getAVIDRootPath(), "python", "templates", "PDC_template.bat")

with workflow.initSession_byCLIargs(expandPaths = True, autoSave = True) as session:
    mapR(ActionTagSelector("CCT"), templateSelector=ActionTagSelector("BPLCT"), outputExt = "ctx.gz", actionTag = "MapCT").do()
    pdc(ActionTagSelector("MapCT"), ActionTagSelector("plan"), ActionTagSelector("struct"), executionBat= pdcTemplatePath, actionTag= "DoseCalc").do()
    #regVar(ActionTagSelector("RegTool")+FormatSelector("MatchPoint"), NR_VARIATIONS, regVarTemplatePath, MEAN, STDDEV, actionTag="RegVarTool", regVariationToolExe = os.path.join("RegVariationTool","RegVariationTool.exe")).do()

    doseAcc(ActionTagSelector("DoseCalc")+FormatSelector(artefactProps.FORMAT_VALUE_VIRTUOS),ActionTagSelector("RegTool")+FormatSelector("MatchPoint"),ActionTagSelector("plan"), actionTag="DoseAcc").do()
    doseMap(ActionTagSelector("DoseCalc")+FormatSelector(artefactProps.FORMAT_VALUE_VIRTUOS),ActionTagSelector("RegTool")+FormatSelector("MatchPoint"), actionTag="DoseMap").do()

    lastFraction = 25
    bioModelCalc(ActionTagSelector("DoseAcc")+TimepointSelector(lastFraction), modelParameters=[0.1, 0.001333], modelName="LQ", actionTag = "BioModelAccumulatedDose").do()
    bioModelCalc(ActionTagSelector("DoseCalc")+FormatSelector(artefactProps.FORMAT_VALUE_VIRTUOS), ActionTagSelector("plan"), modelParameters=[0.1, 0.0333], modelName="LQ", actionTag = "BioModelFractionDose").do()
    bioModelCalc(ActionTagSelector("dose")+FormatSelector(artefactProps.FORMAT_VALUE_VIRTUOS), modelParameters=[0.1, 0.001333], modelName="LQ", actionTag = "BioModelPlannedDose").do()

    doseAcc(ActionTagSelector("BioModelFractionDose"),ActionTagSelector("RegTool")+FormatSelector("MatchPoint"),ActionTagSelector("plan"), operator="*", actionTag="DoseAccBioModel").do()

    #doseTool(ActionTagSelector("dose"),ActionTagSelector("struct"),['RUECKENMARK'], actionTag = "DoseToolPlanned").do()
    #doseTool(ActionTagSelector("DoseAcc"),ActionTagSelector("struct"),['RUECKENMARK'], actionTag = "DoseTool", alwaysDo=True).do()

    #doseStatsWithInterpolationCollector(ActionTagSelector("DoseToolPlanned"), ActionTagSelector("plan"), ['maximum'], actionTag = "DoseStatsPlannedCollector",alwaysDo=True).do()
    #doseStatsCollector(ActionTagSelector("DoseTool"),['maximum'], actionTag = "DoseStatsCollector",alwaysDo=True).do()

    #doseProcessVisualizer(ActionTagSelector("DoseStatsCollector"), ActionTagSelector("DoseStatsPlannedCollector"), None, os.path.join(templatePath, "diagramCSVSource.R"), "Uncertainty Max Dose", "Fractions", "Dose (Gy)", actionTag = "DoseProcessVisualizer", rScriptExe=RSCRIPTEXE, alwaysDo=True).do()
    #doseProcessVisualizer(ActionTagSelector("DoseStatsCollector"), ActionTagSelector("DoseStatsPlannedCollector"), ActionTagSelector("DoseStatsPlannedCollector"), os.path.join(templatePath, "deltaDiagramWithQuantilAndAdditionalDataCSVSource.R"), "Uncertainty Delta-View Max Dose", "Fractions", "Delta Dose (Gy)", actionTag = "DoseProcessVisualizer", rScriptExe=RSCRIPTEXE, alwaysDo=True).do()
    #doseProcessVisualizer(ActionTagSelector("DoseStatsCollector"), ActionTagSelector("DoseStatsPlannedCollector"), ActionTagSelector("DoseStatsPlannedCollector"), os.path.join(templatePath, "boxplotWithAdditionalDataCSVSource.R"), "Uncertainty Max Dose last fraction", "", "Delta Dose (Gy)", actionTag = "DoseProcessVisualizer", rScriptExe=RSCRIPTEXE, alwaysDo=True).do()

