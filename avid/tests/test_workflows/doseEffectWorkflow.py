__author__ = 'hentsch'

import os
import sys

import avid.common.artefact.defaultProps as artefactProps
import avid.common.workflow as workflow
from avid.actions.bioModelCalc import BioModelCalcBatchAction as bioModelCalc
from avid.actions.doseAcc import DoseAccBatchAction as doseAcc
from avid.actions.doseMap import DoseMapBatchAction as doseMap
from avid.actions.matchR import matchRBatchAction as matchR
from avid.actions.mapR import mapRBatchAction as mapR
from avid.common.AVIDUrlLocater import getUtilityPath
from avid.common.AVIDUrlLocater import getAVIDProjectRootPath
from avid.selectors import ActionTagSelector
from avid.selectors import FormatSelector
from avid.selectors import TimepointSelector

__this__ = sys.modules[__name__]

plastimatchParameterFile = os.path.join(getAVIDProjectRootPath(), "templates", "plastimatchTest.txt")
plastimatchAlgorithm = os.path.join(getUtilityPath(), "matchR", "mdra-0-12_PlmParameterFileCLI3DRegistration.dll")
plastimatchDirectory = "C:/Program Files/plastimatch 1.6.4/bin"

with workflow.initSession_byCLIargs(expandPaths = True, autoSave = True) as session:
    plastimatchAlgorithmParameters = {"PlastimatchDirectory" : plastimatchDirectory, "ParameterFilePath" : plastimatchParameterFile}
    matchR(ActionTagSelector("PlCT"), ActionTagSelector("Control"), plastimatchAlgorithm, algorithmParameters=plastimatchAlgorithmParameters, targetIsReference=False, actionTag="matchR").do()
    mapR(ActionTagSelector("Control"), registrationSelector=ActionTagSelector("matchR"), templateSelector=ActionTagSelector("PlCT"), outputExt = "nrrd", actionTag = "MapCT").do()

    doseAcc(ActionTagSelector("dose")+FormatSelector(artefactProps.FORMAT_VALUE_ITK),ActionTagSelector("matchR")+FormatSelector("MatchPoint"),ActionTagSelector("plan"), actionTag="DoseAcc").do()
    doseMap(ActionTagSelector("dose")+FormatSelector(artefactProps.FORMAT_VALUE_ITK),ActionTagSelector("matchR")+FormatSelector("MatchPoint"), actionTag="DoseMap").do()

    lastFraction = 2
    bioModelCalc(ActionTagSelector("DoseAcc")+TimepointSelector(lastFraction), useDoseScaling = False, normalizeFractions= True, planSelector=ActionTagSelector("plan"), modelParameterMapsSelector=ActionTagSelector("parameterMap"), modelName="LQ", actionTag = "BioModelAccumulatedDose").do()
    bioModelCalc(ActionTagSelector("dose")+FormatSelector(artefactProps.FORMAT_VALUE_ITK), useDoseScaling = False, normalizeFractions= False, planLinker=ActionTagSelector("plan"), modelParameterMapsSelector=ActionTagSelector("parameterMap"), modelName="LQ", actionTag = "BioModelFractionDose").do()

    doseAcc(ActionTagSelector("BioModelFractionDose"),ActionTagSelector("matchR")+FormatSelector("MatchPoint"),ActionTagSelector("plan"), operator="*", actionTag="DoseAccBioModel").do()

