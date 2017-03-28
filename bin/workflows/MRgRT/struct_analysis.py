__author__ = 'floca'

import sys
import os
import argparse

import avid.common.workflow as workflow
from avid.common.AVIDUrlLocater import getToolConfigPath
import avid.common.demultiplexer as demux
import avid.common.artefact.defaultProps as artefactProps
from avid.selectors import ActionTagSelector as ATS
from avid.linkers import FractionLinker
from avid.linkers import KeyValueLinker
from avid.linkers import CaseLinker
from avid.actions.mapR import mapRBatchAction as mapR
from avid.actions.matchR import matchRBatchAction as matchR
from avid.actions.voxelizer import VoxelizerBatchAction as Voxelizer
from avid.actions.plmDice import plmDiceBatchAction as plmDice
from avid.actions.doseStatsCollector import DoseStatsCollectorBatchAction as doseStatsCollector
from avid.actions.threadingScheduler import ThreadingScheduler

__this__ = sys.modules[__name__]

#command line parsing
parser = argparse.ArgumentParser()
parser.add_argument('--plmTemplate', default="D:/ISILib/KimKraus_MRgRT_AVID_TestData/plm_commands.txt")
parser.add_argument('--parallel', type=int, default=1)
cliargs, unknown = parser.parse_known_args()

plmDIRConfigPath = cliargs.plmTemplate
multiTaskCount = cliargs.parallel

plmPath = os.path.split(getToolConfigPath('plastimatch'))[0]
regDIPP_rigid_multimodal = os.path.join(os.path.split(getToolConfigPath('matchR'))[0], 'mdra-0-13_DIPP_MultiModal_rigid_default.dll')
regPlm_CLI = os.path.join(os.path.split(getToolConfigPath('matchR'))[0], 'mdra-0-13_PlmParameterFileCLI3DRegistration.dll')

###############################################################################
# general setup selectors for a more readable script
###############################################################################
BPLCTSelector = ATS("BPLCT")
BPLMRSelector = ATS("BPLMR")
fxMRSelector = ATS("fxMR")

BPLCTStructSetSelector = ATS("BPLCT_struct")
BPLMRStructSetSelector = ATS("BPLMR_struct")
fxMRStructSetSelector = ATS("fxMR_struct")

BPLMRPointsSelector = ATS("BPLMR_points")
fxMRPointsSelector = ATS("fxMR_points")

StructsSelector = ATS("Structs")
ControlDoseSelector = ATS("ControlDose")
MappedDoseSelector = ATS("MappedDose")
RegSelector = ATS("Registration")

###############################################################################
# the workflow itself
###############################################################################
with workflow.initSession_byCLIargs(expandPaths=True, autoSave=True) as session:
    reg_MR2CTSelector = matchR(BPLCTSelector, BPLMRSelector, algorithm=regDIPP_rigid_multimodal, actionTag = 'reg_MR2CT', scheduler = ThreadingScheduler(multiTaskCount)).do().tagSelector
    mappedMR2CTSelector = mapR(BPLMRSelector, reg_MR2CTSelector, BPLCTSelector, actionTag="MappedMR2CT", scheduler = ThreadingScheduler(multiTaskCount)).do().tagSelector
    mappedMRPoints2CTSelector = mapR(BPLMRPointsSelector, reg_MR2CTSelector, actionTag="MappedMRPoints2CT", scheduler = ThreadingScheduler(multiTaskCount)).do().tagSelector

    reg_MR2CT2fxMRSelector = matchR(fxMRSelector, mappedMR2CTSelector, targetPointSetSelector=fxMRPointsSelector, movingPointSetSelector=mappedMRPoints2CTSelector, algorithm=regPlm_CLI, algorithmParameters={'PlastimatchDirectory':plmPath, 'ParameterFilePath': plmDIRConfigPath}, actionTag = 'reg_MR2CT2fxMR', scheduler = ThreadingScheduler(multiTaskCount)).do().tagSelector
    mapR(mappedMR2CTSelector, reg_MR2CT2fxMRSelector, fxMRSelector, regLinker = CaseLinker(), templateRegLinker = FractionLinker(), actionTag="MappedMR2CT2fxMR", propInheritanceDict = {artefactProps.TIMEPOINT:'templateImage'}, scheduler = ThreadingScheduler(multiTaskCount)).do()
    mapR(BPLCTSelector, reg_MR2CT2fxMRSelector, fxMRSelector, regLinker = CaseLinker(), templateRegLinker = FractionLinker(), actionTag="MappedCT2fxMR", propInheritanceDict = {artefactProps.TIMEPOINT:'templateImage'}, scheduler = ThreadingScheduler(multiTaskCount)).do()

    CTMaskSelector = Voxelizer(BPLCTStructSetSelector, BPLCTSelector, booleanMask = True, allowIntersections = True, actionTag='CTMask', scheduler = ThreadingScheduler(multiTaskCount)).do().tagSelector
    MRMaskSelector = Voxelizer(BPLMRStructSetSelector, BPLMRSelector, booleanMask=True, allowIntersections=True, actionTag='MRMask', scheduler = ThreadingScheduler(multiTaskCount)).do().tagSelector
    fxMRMaskSelector = Voxelizer(fxMRStructSetSelector, fxMRSelector, referenceLinker = FractionLinker(), booleanMask=True, allowIntersections=True, actionTag='fxMRMask', scheduler = ThreadingScheduler(multiTaskCount)).do().tagSelector

    mappedCTMaskSelector = mapR(CTMaskSelector, reg_MR2CT2fxMRSelector, fxMRSelector, regLinker = CaseLinker(), templateRegLinker = FractionLinker(), interpolator = "nn", actionTag="mappedCTMask2fxMR", propInheritanceDict = {artefactProps.TIMEPOINT:'templateImage'}, scheduler = ThreadingScheduler(multiTaskCount)).do().tagSelector

    mappedMRMask2CTSelector = mapR(MRMaskSelector, reg_MR2CTSelector, BPLCTSelector, interpolator = "nn", actionTag="mappedMRMask2CT", scheduler = ThreadingScheduler(multiTaskCount)).do().tagSelector
    mappedMRMaskSelector = mapR(mappedMRMask2CTSelector, reg_MR2CT2fxMRSelector, fxMRSelector, regLinker = CaseLinker(), templateRegLinker = FractionLinker(), interpolator = "nn", actionTag="mappedMRMask2fxMR", propInheritanceDict = {artefactProps.TIMEPOINT:'templateImage'}, scheduler = ThreadingScheduler(multiTaskCount)).do().tagSelector

    structLinker = FractionLinker() + KeyValueLinker(artefactProps.OBJECTIVE)
    plmDice(fxMRMaskSelector, mappedCTMaskSelector, structLinker, 'CTDice', scheduler = ThreadingScheduler(multiTaskCount)).do()
    plmDice(fxMRMaskSelector, mappedMRMaskSelector, structLinker, 'MRDice', scheduler = ThreadingScheduler(multiTaskCount)).do()

    #collect everything into tables
    structSelectors = demux.getSelectors(artefactProps.OBJECTIVE, ATS('CTDice'))
    for structID in structSelectors:
        doseStatsCollector(structSelectors[structID],['DICE', 'Hausdorff distance'], rowKey = artefactProps.TIMEPOINT,
                           columnKey = artefactProps.CASE, actionTag = 'Stats_CT_'+structID, alwaysDo = True).do()

    structSelectors = demux.getSelectors(artefactProps.OBJECTIVE, ATS('MRDice'))
    for structID in structSelectors:
        doseStatsCollector(structSelectors[structID], ['DICE', 'Hausdorff distance'], rowKey=artefactProps.TIMEPOINT,
                           columnKey=artefactProps.CASE, actionTag='Stats_MR_' + structID, alwaysDo=True).do()
