# AVID
# Automated workflow system for cohort analysis in radiology and radiation therapy
#
# Copyright (c) German Cancer Research Center,
# Software development for Integrated Diagnostic and Therapy (SIDT).
# All rights reserved.
#
# This software is distributed WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.
#
# See LICENSE.txt or http://www.dkfz.de/en/sidt/index.html for details.

from builtins import str
from builtins import range
import collections
import os

from avid.common.osChecker import checkAndCreateDir
from avid.common import dvhTxtFileLoader
from avid.common import doseToolResultLoader
from avid.common.flatFileEntryGenerator import FlatFileEntryGenerator
import avid.common.flatFileDictEntries as FFDE

ACTION_TAG    = str()

def do(workflow, DVHSelector, DoseStatsSelector, actionTag="DVHCollector"):
    """Action extracts the defined DVH values
     and stores them in a csv file.
    """
    global ACTION_TAG
    ACTION_TAG = actionTag
    """Create the directories"""
    xmlEntryOutPath=os.path.join(os.path.join(workflow.outPath,actionTag),"result")
    checkAndCreateDir(xmlEntryOutPath)
    FFEGobj = FlatFileEntryGenerator()

    allDVHSelections = DVHSelector.getFilteredContainer(workflow.artefacts)
    fractions = _getFractions(allDVHSelections)

    for i in range(0,workflow.numberOfPatients()):
      DoseStatsSelector.updateKeyValueDict({FFDE.CASE:str(i)})
      DoseStatsList = DoseStatsSelector.getFilteredContainer(workflow.artefacts)

      if DoseStatsList:
        firstDoseStat = DoseStatsList[0]
        maxVolCcm = _getVolume(firstDoseStat[FFDE.URL])
      else:
        raise

      for fraction in range(_getMin(fractions),_getMax(fractions)+1):
        DVHSelector.updateKeyValueDict({FFDE.CASE:str(i), FFDE.TIMEPOINT:fraction})
        DVHList = DVHSelector.getFilteredContainer(workflow.artefacts)
        doseAllVariations = []
        volumeAllVariations = []
        DVHType = "cum"
        """Iterate over each found DVH file"""
        for DVH in DVHList:
          aDVHDictAbs = _parseDVH(DVH[FFDE.URL])
          aDVHDictRel = _normalize(aDVHDictAbs, maxVolCcm)
          listDose = list(aDVHDictRel.keys())
          listVolume = list(aDVHDictRel.values())
          if aDVHDictAbs.dvhType==dvhTxtFileLoader.DVHType.Cumulative:
            DVHType = "cum"
          else:
            DVHType = "diff"
          doseAllVariations.append(listDose)
          volumeAllVariations.append(listVolume)

        DVHDoseFilename = os.path.join(xmlEntryOutPath, "DVHDose_"+DVHType+"-"+str(fraction)+".csv")
        _writeToCSV(doseAllVariations, None, DVHDoseFilename)
        workflow.artefacts = FFEGobj.addCSVResultToContainer(workflow.artefacts, str(i), str(fraction), "DVHDose_"+DVHType,\
                                                                 DVHDoseFilename, ACTION_TAG)

        DVHVolumeFilename = os.path.join(xmlEntryOutPath, "DVHVolume_"+DVHType+"-"+str(fraction)+".csv")
        _writeToCSV(volumeAllVariations, None, DVHVolumeFilename)

        workflow.artefacts = FFEGobj.addCSVResultToContainer(workflow.artefacts, str(i), str(fraction), "DVHVolume_"+DVHType,\
                                                                 DVHVolumeFilename, ACTION_TAG)

def _parseDVH(filename):
  resultContainer = dvhTxtFileLoader.parseFile(filename)
  return resultContainer

def _normalize(DVHResultContainer, maxVolCcm):
  """Normalizes the DVH from DVH parser as follows:
     absolute dose (in Gy) is computed from the current index and deltaD
     relative volume is computed from given maxVolCcm, deltaV and the current DVH entry
     Returns:
     a dict with key dose and value volume
  """
  DVHData = DVHResultContainer.dvhData
  deltaD = DVHResultContainer.deltaDose
  deltaV = DVHResultContainer.deltaVolume
  absoluteValuesGyCcm = collections.OrderedDict()
  for index, DVHEntry in enumerate(DVHData) :
    absDose = index*deltaD
    absVolume = DVHEntry*deltaV
    absoluteValuesGyCcm[absDose] = absVolume / maxVolCcm
  return absoluteValuesGyCcm

def _getVolume(filename):
    """get relevant values from file (DoseStatistics)"""
    resultContainer = doseToolResultLoader.parseFile(filename)
    volume = float(resultContainer.getDVHValue("volume irradiated"))
    return volume
             
def _writeToCSV(doseList, header, filename, delimiter=";"):
    with open(filename, 'w') as file:
      '''write header (x-axis: fractions)'''
      if header is not None:
        ending = delimiter
        for ele in header:
          if header[-1] is ele:
            ending="\n"
          file.write(str(ele) + ending)

      '''write given dose values'''

      for instance in doseList:
        ending = delimiter
        for fraction in instance:
          if instance[-1] is fraction:
            ending="\n"
          file.write(str(fraction)+ending)

def _getFractions(list):
  return [int(element[FFDE.TIMEPOINT]) for element in list]

def _getMin(list):
  return min(list)

def _getMax(list):
  return max(list)