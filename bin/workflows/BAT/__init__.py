from avid.common import artefact
__author__ = 'floca'

import sys
import os
import argparse

import avid.common.workflow as workflow
import avid.common.artefact.defaultProps as artefactProps
from avid.common.AVIDUrlLocater import getAVIDProjectRootPath
from avid.selectors import ActionTagSelector
from avid.selectors import FormatSelector
from avid.selectors import TimepointSelector
from avid.selectors import ObjectiveSelector
from avid.selectors import KeyValueSelector
from avid.selectors import TypeSelector
from avid.actions.mapR import mapRBatchAction as mapR
from avid.actions.regTool import regToolBatchAction as regTool
from avid.actions.regVarTool import RegVarToolBatchAction as regVarTool
from avid.actions.bat import CombineDataBatchAction as combineData
from avid.actions.bat import FFMapsBatchAction as ffMaps
from avid.actions.bat import BATMaskBatchAction as batMask
from avid.actions.bat import BATCriteriaBatchAction as batCriteria
from avid.actions.fitting import LinearFitBatchAction as linearFit
from avid.actions.imageAcc import ImageAccBatchAction as imageAcc
from avid.actions.cleanWorkflow import cleanWorkflowBatchAction as clean
from avid.actions.threadingScheduler import ThreadingScheduler
import avid.common.demultiplexer as demux

__this__ = sys.modules[__name__]

#command line parsing
parser = argparse.ArgumentParser()
parser.add_argument('--variationParameters', nargs="*", default=[0.0, 0.5])
parser.add_argument('--nVariations', type=int, default=20)
cliargs, unknown = parser.parse_known_args()

if cliargs.nVariations is not None:
    nVariations = cliargs.nVariations
if cliargs.variationParameters is not None:
    variationParameters = cliargs.variationParameters

#general setup variables and selectors for a more readable script
regTemplate = os.path.join(getAVIDProjectRootPath(), "templates", "DIPP_FastSymmetricForcesDemons.reg.xml")
regDummyTemplate = os.path.join(getAVIDProjectRootPath(), "templates", "Dummy3D.reg.xml")
ALGORITHMDLL = "C:/dev/AVID/trunk/Utilities/RegVarTool/mdra-0-12_RegVariationKernelRandomGaussianTPS.dll"
PARAMETERS = {"Mean" : "0.0", "StandardDeviation" : "3.0", "GridSize" : "5"}

matlabScriptPath = r"D:\Projects\BAT\Matlab"

with workflow.initSession_byCLIargs(expandPaths = True, autoSave = True) as session:
  session.actionTools['matlab'] = r"C:\Program Files\MATLAB\R2015a\bin\matlab.exe"
  session.actionTools['GenericFittingMiniApp'] = r"C:\dev\DIPP\Installer\DIPP-2016.03.9000\bin\GenericFittingMiniApp.exe"
  
  #we perform the analysis case wise to reduce the amount of needed temporary diskspace
  caseDict = demux.getSelectors(artefactProps.CASE)
  for caseID in caseDict:
    #####################################
    #selector definition
    relevantCaseSelector = caseDict[caseID]
    WaterSelector = ActionTagSelector("water") + relevantCaseSelector
    WaterRefSelector = WaterSelector+KeyValueSelector("target", "True")
    WaterFollowUpSelector = WaterSelector+KeyValueSelector("target", "True", negate=True)
    FatSelector = ActionTagSelector("fat") + relevantCaseSelector
    FatRefSelector = FatSelector+KeyValueSelector("target", "True")
    FatFollowUpSelector = FatSelector+KeyValueSelector("target", "True", negate=True)
    RegistrationSelector = ActionTagSelector("Registration")+FormatSelector("MatchPoint") + relevantCaseSelector
    FFUpSelector = ActionTagSelector("FFMap") + ObjectiveSelector("complete") + relevantCaseSelector
    FF623Selector = ActionTagSelector("FFMap") + ObjectiveSelector("cooling") + relevantCaseSelector
    SlopeSelector = ActionTagSelector("FF_Fit") + ObjectiveSelector("slope") + relevantCaseSelector
    BATMaskSelector = ActionTagSelector("BATMask")+relevantCaseSelector
    BATCriteriaLogicalSelector = ActionTagSelector("BATCriteria") + ObjectiveSelector("logical") + relevantCaseSelector

    #####################################
    #the workflow itself
    batMask(ActionTagSelector("lung_up")+ relevantCaseSelector, ActionTagSelector("thorax_up")+ relevantCaseSelector, matlabScriptPath, actionTag = "BATMask").do()

    regTool(WaterRefSelector, WaterFollowUpSelector, regTemplate, targetIsReference=False, actionTag = "Registration", scheduler = ThreadingScheduler(10)).do()
    #generate dummy registrations for the reference as well to correctly handle the reg variations
    regTool(WaterRefSelector, WaterRefSelector, regDummyTemplate, targetIsReference=False, actionTag = "Registration").do() 
  
    regVarTool(RegistrationSelector, nVariations, ALGORITHMDLL, PARAMETERS, WaterRefSelector, actionTag="RegVarTool", regVarToolExe = os.path.join("RegVarTool","RegVarTool.exe"), scheduler = ThreadingScheduler(8)).do()
  
    mapR(WaterSelector, registrationSelector = ActionTagSelector("RegVarTool"),  templateSelector=WaterRefSelector, outputExt = "nrrd", actionTag = "Watter_Mapped", mapRExe = os.path.join("mapR","mapR.exe"), scheduler = ThreadingScheduler(64)).do()
    mapR(FatSelector, registrationSelector = ActionTagSelector("RegVarTool"),  templateSelector=WaterRefSelector, outputExt = "nrrd", actionTag = "Fat_Mapped", mapRExe = os.path.join("mapR","mapR.exe"), scheduler = ThreadingScheduler(64)).do()
  
    combineData(ActionTagSelector("Watter_Mapped")+relevantCaseSelector, matlabScriptPath, actionTag = "Watter4D", scheduler = ThreadingScheduler(4)).do()
    combineData(ActionTagSelector("Fat_Mapped")+relevantCaseSelector, matlabScriptPath, actionTag = "Fat4D", scheduler = ThreadingScheduler(4)).do()
      
    ffMaps(ActionTagSelector("Watter4D")+relevantCaseSelector, ActionTagSelector("Fat4D")+relevantCaseSelector, matlabScriptPath, actionTag = "FFMap", scheduler = ThreadingScheduler(4)).do()      
 
    linearFit(FF623Selector, BATMaskSelector, actionTag = "FF_Fit", scheduler = ThreadingScheduler(4)).do()
             
    batCriteria(FFUpSelector, BATMaskSelector, SlopeSelector, matlabScriptPath, actionTag = "BATCriteria").do()
      
    imageAcc(BATCriteriaLogicalSelector, actionTag = "BAT_Probabilitic", imageSplitProperty=artefactProps.CASE).do()
    
    clean(ActionTagSelector("RegVarTool")+TypeSelector(artefactProps.TYPE_VALUE_RESULT)).do()
    clean(ActionTagSelector("Watter_Mapped"),True).do()
    clean(ActionTagSelector("Fat_Mapped"),True).do()
    clean(ActionTagSelector("Watter4D"),True).do()
    clean(ActionTagSelector("Fat4D"),True).do()
    clean(ActionTagSelector("FFMap"),True).do()  
