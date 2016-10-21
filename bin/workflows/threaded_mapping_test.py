__author__ = 'floca'

import sys
import os
import argparse

from avid.common import artefact
import avid.common.workflow as workflow
import avid.common.artefact.defaultProps as artefactProps
from avid.common.AVIDUrlLocater import getAVIDProjectRootPath
from avid.common.AVIDUrlLocater import getUtilityPath
from avid.selectors import ActionTagSelector
from avid.actions.mapR import mapRBatchAction as mapR
from avid.actions.regVarTool import RegVarToolBatchAction as regVarTool
from avid.actions.threadingScheduler import ThreadingScheduler
from avid.common.artefact import generateArtefactEntry as generateArtefactEntry

__this__ = sys.modules[__name__]

#command line parsing
parser = argparse.ArgumentParser()
parser.add_argument('--variationParameters', nargs="*", default=[0.0, 0.5])
parser.add_argument('--nVariations', type=int, default=3000)
cliargs, unknown = parser.parse_known_args()

if cliargs.nVariations is not None:
    nVariations = cliargs.nVariations
if cliargs.variationParameters is not None:
    variationParameters = cliargs.variationParameters

#general setup variables and selectors for a more readable script
regIdentityPath = os.path.join(getAVIDProjectRootPath(), "avid", "tests", "data", "mapRTest", "Identity.mapr")
imagePath = os.path.join(getAVIDProjectRootPath(), "avid", "tests", "data", "mapRTest", "MatchPointLogo.mhd")
ALGORITHMDLL = os.path.join(getUtilityPath(),"RegVarTool","mdra-0-12_RegVariationKernelRandomGaussianTPS.dll")
PARAMETERS = {"Mean" : str(variationParameters[0]), "StandardDeviation" : str(variationParameters[1]), "GridSize" : "5"}

with workflow.initSession_byCLIargs(expandPaths = True, autoSave = True) as session:
  
    entry = generateArtefactEntry('Case1', None, 0, 'Reg', artefactProps.TYPE_VALUE_RESULT, artefactProps.FORMAT_VALUE_MATCHPOINT, regIdentityPath)
    session.inData.append(entry)
    entry = generateArtefactEntry('Case1', None, 0, 'Input', artefactProps.TYPE_VALUE_RESULT, artefactProps.FORMAT_VALUE_ITK, imagePath)
    session.inData.append(entry)
      
    regVarTool(ActionTagSelector("Reg"), nVariations, ALGORITHMDLL, PARAMETERS, ActionTagSelector("Input"), actionTag="RegVarTool", scheduler = ThreadingScheduler(80)).do() 
    mapR(ActionTagSelector("Input"), registrationSelector = ActionTagSelector("RegVarTool"),  templateSelector=ActionTagSelector("Input"), outputExt = "nrrd", actionTag = "Mapped", scheduler = ThreadingScheduler(64)).do()
