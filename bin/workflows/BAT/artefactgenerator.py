__author__ = 'floca'

import sys
import os
import argparse
import ConfigParser

from avid.common.artefact.crawler import DirectoryCrawler
import avid.common.artefact.defaultProps as artefactProps
from avid.common.artefact.generator import generateArtefactEntry
from avid.common.artefact.fileHelper import saveArtefactList_xml as saveArtefactList

targetID = None
coolstartID = None
coolendID = None


def BATFileFunction(pathParts, fileName, fullPath):
  '''Functor to generate an artefact for a file stored with the BAT project
  storage conventions.'''
  result = None
  name, ext = os.path.splitext(fileName)

  if ext ==".ini":
    #ini file just save the infos for the related "real" artefacts
    
    config = ConfigParser.ConfigParser()
    config.read(fullPath)

    global targetID
    global coolstartID
    global coolendID
    
    targetID = int(config.get('images','target'))
    coolstartID = int(config.get('images','coolstart'))
    coolendID = int(config.get('images','coolend'))
    
  elif ext ==".nrrd":
    #the normal data
    case = pathParts[0]
    tag = pathParts[1]
    if tag == "Masks":
      tag = name
    
    timepoint = 0
    try:
      timepoint = int(name.split('_')[-1])
    except:
      pass
      
    targetflag = False
    if targetID == timepoint:
      targetflag = True
      
    result = generateArtefactEntry(case, None, timepoint, tag, artefactProps.TYPE_VALUE_RESULT, artefactProps.FORMAT_VALUE_ITK, fullPath, coolendID = coolendID, coolstartID = coolstartID, targetID = targetID, target = targetflag)
    
  return result
  
  
def generateArtefactList(root):
  crawler = DirectoryCrawler(root, BATFileFunction)  
  
  return crawler.getArtefacts()


if __name__ == "__main__":
  
  parser = argparse.ArgumentParser()
  parser.add_argument('root')
  parser.add_argument('output')
  cliargs, unknown = parser.parse_known_args()

  artefacts = generateArtefactList(cliargs.root)
  
  saveArtefactList(cliargs.output, artefacts)
