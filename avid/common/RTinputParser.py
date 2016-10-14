#################################################
#
#################################################

import argparse, csv
import artefact.defaultProps as artefactProps


parser = argparse.ArgumentParser()
parser.add_argument('-if', '--inFile')
parser.add_argument('-of', '--outputFolder')
parser.add_argument('-tf', '--templateFolder')
parser.add_argument('-n', '--patientName')
parser.add_argument('-a', '--analysisType')
parser.add_argument('-v', '--variations')
parser.add_argument('-sf', '--structuresFile')
parser.add_argument('-gf', '--gaussianParametersFile')
parser.add_argument('-p', '--plannedFractions')

_args = parser.parse_args()
_inputDataObject = list(dict(),)

def generateInputDataObject():
  ' generates a list of dictionaries containing the information of the input file (args.if)'
  global _inputDataObject
  del _inputDataObject[:]
  global _args 
  f = open(_args.inFile, 'r')
  for line in f:
    if line[0] != "#":
      listedline = line.strip().split(';') # split around the = sign
      if len(listedline) > 1:
        _inputDataObject += __createDict(listedline), 
          #_inputDataObject[listedline[0]] = listedline[1]
  return _inputDataObject

def generateStructureList():
  with open(_args.structuresFile, 'r') as f:
    reader = csv.reader(f, delimiter=';')
    aList = list(reader)
  return aList

def generateGaussianParametersList():
  with open(_args.gaussianParametersFile, 'r') as f:
    reader = csv.reader(f, delimiter=';')
    stringList = list(reader)
  floatList=[]
  for ele in stringList:
    floatList.append([float(ele[0]), float(ele[1])])
  return floatList
        
        
def getInputDataObject():
  ' returns the list which contains the input data. \
    Each line of the input file represents a information entry.\
    Each line is stored in a list object, all the objects(lines) are stored in a list of tuples'
  global _inputDataObject
  return _inputDataObject
  
  
def __createDict(listedline):
  ' generates a dictionary containing the information of one input line (args.if)'
  outDict = dict()
  for no,entry in enumerate(listedline):
    if no == 0:
      outDict[artefactProps.ID] = entry
    elif no == 1:
      outDict[artefactProps.CASE] = entry
    elif no == 2:
      outDict[artefactProps.TIMEPOINT] = entry
    elif no == 3:
      outDict[artefactProps.CASEINSTANCE] = entry
    elif no == 4:
      outDict[artefactProps.ACTIONTAG] = entry
    elif no == 5:
      outDict[artefactProps.TYPE] = entry
    elif no == 6:
      outDict[artefactProps.FORMAT] = entry
    elif no == 7:
      outDict[artefactProps.URL] = entry
    else:
      outDict[str(no)] = entry
  return outDict
