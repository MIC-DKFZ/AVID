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

import logging
import shutil
import re
import os


logger = logging.getLogger(__name__)

KEY_CREATED_BY = "created_by"
KEY_CREATED_ON = "created_on"
KEY_PATIENT_NAME = "patient_name"
KEY_DOSE_CALC_BY = "dose_calc_by"
KEY_DOSE_CALC_ON = "dose_calc_on"
KEY_DOSE_FILE = "dose_file"
KEY_DOSE_CALC_BASE = "dose_calc_base"
KEY_PRESCRIBED_DOSE = "prescribed_dose"
KEY_NORM_DOSE = "norm_dose"
KEY_MONITOR_UNITS = "monitor_units"
KEY_NUM_FRACTIONS = "num_fractions"
KEY_REL_REF_DOSE = "rel_ref_dose"


def getFileExtensions(path):
  '''special method that returns the complete virtuos extension. It handles the
  fact that the files could end with ".gz" and then the next extension is also
  needed. (e.g. ".ctx.gz")'''
  rest, ext = os.path.splitext(path)
  if ext == os.extsep+"gz":
    #compressed file -> have to remove
    ext = os.path.splitext(rest)[1]+ext
    
  return ext


def stripFileExtensions(path):
  '''special method that returns the path striped by the complete virtuos
  extension. In contrast to os.path.splittext it handles the
  fact that the files could end with ".gz" and then the next extension is also
  needed. (e.g. ".ctx.gz")'''
  rest, ext = os.path.splitext(path)
  if ext == os.extsep+"gz":
    #compressed file -> have to remove
    rest = os.path.splitext(rest)[0]
    
  return rest


def isVirtuosFile(path):
  '''checks the passed path if it points to a virtuos file type.'''
  ext = getFileExtensions(path)

  result = False  
  if ext in [os.extsep+"ctx", os.extsep+"dos", os.extsep+"pln",
             os.extsep+"ctx"+os.extsep+"gz", os.extsep+"dos"+os.extsep+"gz"]:
    result = True
  
  return result


def createPlanPatternDictionary():
  '''Creates a dictionary for extraction and manipulation of data in virtuos plan files
  The key of the dictionary is the value ID that is handled. The value of the dictionary entry
  is a tuple. First tuple element is the regular expression that describes the line that
  contains the data. The regular expression is designed such a way that it the first match group
  always specifies the value itself. The second tuple element is the key you may use to rewrite/
  alter the plan file''' 
  patterns = dict()
  patterns[KEY_CREATED_BY] =  ('(?:^Created\s*by\s*)(.*)$','Created by                          ')                
  patterns[KEY_CREATED_ON] =  ('(?:^Created\s*on\s*)(.*)$','Created on                          ') 
  patterns[KEY_PATIENT_NAME] =  ('(?:^Name\s*of\s*Patient\s*)(.*)$','Name of Patient                     ') #^Name\s*of\s*Patient\s*(.*)$
  patterns[KEY_DOSE_CALC_BY] =  ('(?:^Dose\s*Calculated\s*by\s*)(.*)$','Dose Calculated by                  ')
  patterns[KEY_DOSE_CALC_ON] =  ('(?:^Dose\s*Calculated\s*on\s*)(.*)$','Dose Calculated on                  ')                  
  patterns[KEY_DOSE_FILE] =  ('(?:^Dose\s*File\s*)(.*)$','Dose File                           ')
  patterns[KEY_DOSE_CALC_BASE] =  ('(?:^Dose\s*Calculation\s*Based\s*on\s*)(.*)$','Dose Calculation Based on           ')
  patterns[KEY_PRESCRIBED_DOSE] =  ('(?:^\s*Prescribed\s*Dose  \s*)(.*)$','  Prescribed Dose                   ')
  patterns[KEY_NORM_DOSE] =  ('(?:^\s*Normalisation\sDose\s*)(.*)$','  Normalisation Dose                ')
  patterns[KEY_MONITOR_UNITS] =  ('(?:^\s*Monitor\sUnits\s*)(.*)$','  Monitor Units                   ')
  patterns[KEY_NUM_FRACTIONS] =  ('(?:^\s*No\s*of\s*Fractions\s*)(.*)$','  No of Fractions                   ')
  patterns[KEY_REL_REF_DOSE] =  ('(?:^\s*Relative reference dose value \(cube\/ref\. point\):\s*)(.*)$','Relative reference dose value (cube/ref. point): ')
  return patterns 

def getValueFromPlan(planStr, key):
  '''extracts the first found value of the passed key from the plan file content string.
  @param planStr String containing the content of a plan file
  @param key Key of the key value pair.
  @pre key must be a key present in the result of createPlanPatternDictionary
  @return the value of the key. If key is not present None will be returned.'''
  patterns = createPlanPatternDictionary()
  
  if key not in patterns:
    logger.error("Cannot get plan value. Key "+str(key)+" is unkown.")
    raise RuntimeError("Cannot get plan value. Key "+str(key)+" is unkown.")
  
  matches = re.search(patterns[key][0], planStr, flags=re.MULTILINE)
  
  result = None
  if matches:
    result = matches.group(1)
    logger.debug("Found values in plan. key = %s; values = %s",key, result)
    result = result.strip()
  
  return result
  
def getValuesFromPlan(planStr, key):
  '''extracts all values of the passed key from the plan file content string.
  @param planStr String containing the content of a plan file
  @param key Key of the key value pair.
  @pre key must be a key present in the result of createPlanPatternDictionary
  @return the list of values of the key. If key is not present the list is empty.'''
  patterns = createPlanPatternDictionary()
  
  if key not in patterns:
    logger.error("Cannot get plan value. Key "+str(key)+" is unkown.")
    raise RuntimeError("Cannot get plan value. Key "+str(key)+" is unkown.")
  
  matches = re.findall(patterns[key][0], planStr, flags=re.MULTILINE)
  logger.debug("Found values in plan. key = %s; values = %s",key, matches)
  
  return matches

def setValueInPlan(planStr, key, value):
  '''(re)sets the value of the passed key in the plan file content string and returns the
  modified string.
  @param planStr String containing the content of a plan file
  @param key Key of the key value pair.
  @param value value that should be set.
  @pre key must be a key present in the result of createPlanPatternDictionary
  @return the manipulated string'''
  patterns = createPlanPatternDictionary()
  
  if key not in patterns:
    raise RuntimeError("Cannot get plan value. Key "+str(key)+" is unkown.")
  
  logger.debug("Set plan value: pattern="+patterns[key][0]+", substitute="+patterns[key][1])
  newStr = re.sub(patterns[key][0], patterns[key][1]+str(value), planStr, flags=re.MULTILINE)
  
  return newStr


def readFile(planFile):
  '''reads a given file into a string and returns the string'''
  with open(planFile, 'r') as file_handle:
    return file_handle.read()

  
def writeFile(planFile, content):
  '''Writes content to a given file'''
  with open(planFile, 'w') as file_handle:
    file_handle.write(str(content))
  
    
def calculateNormDoseCorrected(newNormDose, newMU, oldMU, newRelRefDose, oldRelRefDose):
  
  if not newNormDose == 0:
    if oldMU == 0:
      logger.error("Cannot calculate corrected Norm Dose. Old monitor units are zero.")
    if newRelRefDose == 0:
      logger.error("Cannot calculate corrected Norm Dose. New relative reference dose value is zero.")
    correctedDose = newNormDose * (newMU / oldMU) * (oldRelRefDose / newRelRefDose)
  else:
    correctedDose = 0
    
  return correctedDose


def normalizePlanFile(newPlanFile, refPlanFile):
  '''normalizes dose values of the new plan (its recalculated dose) according to the original plan'''
  newPlanStr = readFile(newPlanFile)
  refPlanStr = readFile(refPlanFile)
  
  newNormDose = float(getValueFromPlan(newPlanStr, KEY_NORM_DOSE))
  newMU = float(getValueFromPlan(newPlanStr, KEY_MONITOR_UNITS))
  oldMU = float(getValueFromPlan(refPlanStr, KEY_MONITOR_UNITS))
  newRelRefDose = float(getValueFromPlan(newPlanStr, KEY_REL_REF_DOSE))
  oldRelRefDose = float(getValueFromPlan(refPlanStr, KEY_REL_REF_DOSE))
  
  correctedDose = calculateNormDoseCorrected(newNormDose, newMU, oldMU, newRelRefDose, oldRelRefDose)

  newPlanStr = setValueInPlan(newPlanStr, KEY_NORM_DOSE, correctedDose)
  
  writeFile(newPlanFile, newPlanStr)


def resetPlanFile(planFile):
  ''' Takes a plan file and resets all entries defined by pdc++.
  This is needed to reuse the plan file for dose calculation.''' 
  file_string = readFile(planFile)
     
  file_string = setValueInPlan(file_string, KEY_PATIENT_NAME, "unkown")
  file_string = setValueInPlan(file_string, KEY_DOSE_CALC_BY, "")
  file_string = setValueInPlan(file_string, KEY_DOSE_CALC_ON, "")
  file_string = setValueInPlan(file_string, KEY_DOSE_FILE, "")
  file_string = setValueInPlan(file_string, KEY_CREATED_BY, "")
  file_string = setValueInPlan(file_string, KEY_CREATED_ON, "")
  file_string = setValueInPlan(file_string, KEY_DOSE_CALC_BASE, "")
  
  writeFile(planFile, file_string)


def createBatchFileReplacePatternList(rootDir, patient, image, struct, planNr, dataDir, patientDir, deviceDir):
  patternList = list()
  patternList.append(('^set\s*ROOT_DIR=.*$','set ROOT_DIR='+rootDir))
  patternList.append(('^set\s*DEVICE_DIR=.*$','set DEVICE_DIR='+deviceDir))
  patternList.append(('^set\s*pat=.*$','set pat='+patient))
  patternList.append(('^set\s*img=.*$','set img='+image))
  patternList.append(('^set\s*vdx=.*$','set vdx='+struct))           
  patternList.append(('^set\s*plan_no=.*$','set plan_no='+planNr))
  patternList.append(('^set\s*DATA_DIR=.*$','set DATA_DIR='+dataDir))
  patternList.append(('^set\s*PATIENT_DIR=.*$','set PATIENT_DIR='+patientDir)) 
  return patternList 


def generateBatchFile(batchFile, template, rootDir, patient, image, struct, planNr, dataDir, patientDir, deviceDir):    
  ''' open and adapt batch script content for system call ''' 
  shutil.copyfile(template, batchFile)
  try:
    file_string = readFile(batchFile)
    
    patternList = createBatchFileReplacePatternList(rootDir, patient, image, struct, planNr, dataDir, patientDir, deviceDir)  
    
    # Use RE package to allow for replacement (also allowing for (multiline) REGEX)
    for pattern in patternList:
      logger.debug("Test:pattern="+pattern[0]+", substitute="+pattern[1])
      matches = re.findall(pattern[0], file_string, flags=re.MULTILINE)
      for match in matches:
        file_string = file_string.replace(match, pattern[1])
      
    file_string += "\nEXIT"
    
    writeFile(batchFile, file_string)

  except BaseException as err:
    logger.error("Unkown error. Adapting the new batch file failed. Reason: %s", err)
    raise
  
  except:
    logger.error("Unkown error. Adapting the new batch file failed. Reason: unkown")
    raise  