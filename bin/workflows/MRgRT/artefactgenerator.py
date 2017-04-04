__author__ = 'floca'

import os
import argparse
import re

from avid.common.artefact.crawler import DirectoryCrawler
import avid.common.artefact.defaultProps as artefactProps
from avid.common.artefact.generator import generateArtefactEntry
from avid.common.artefact.fileHelper import saveArtefactList_xml as saveArtefactList
import avid.externals.fcsv as fcsv
import avid.externals.matchPoint as matchpoint

def determineFraction(name):
    matches = re.search('_frac(\d+)_', name, flags=re.MULTILINE)
    result = None
    if matches:
        result = int(matches.group(1))
    return result

def mrgrtFileFunction(pathParts, fileName, fullPath):
    '''Functor to generate an artefact for a file stored with the BAT project
    storage conventions.'''
    result = None
    name, ext = os.path.splitext(fileName)
    case = pathParts[0]

    timepoint = determineFraction(pathParts[-1])

    if ext ==".dcm":
        if not timepoint is None:
            #fraction directory
            if name.startswith('RS_'):
                result = generateArtefactEntry(case, None, timepoint, 'fxMR_struct', artefactProps.TYPE_VALUE_RESULT,
                                               artefactProps.FORMAT_VALUE_DCM, fullPath)
            else:
                result = generateArtefactEntry(case, None, timepoint, 'fxMR', artefactProps.TYPE_VALUE_RESULT,
                                             artefactProps.FORMAT_VALUE_DCM, fullPath)

        if pathParts[-1] == 'BPL_CT':
            if name.startswith('RS_'):
                result = generateArtefactEntry(case, None, 0, 'BPLCT_struct', artefactProps.TYPE_VALUE_RESULT,
                                               artefactProps.FORMAT_VALUE_DCM, fullPath)
            else:
                result = generateArtefactEntry(case, None, 0, 'BPLCT', artefactProps.TYPE_VALUE_RESULT,
                                               artefactProps.FORMAT_VALUE_DCM, fullPath)

        if pathParts[-1] == 'BPL_MR':
            if name.startswith('RS_'):
              result = generateArtefactEntry(case, None, 0, 'BPLMR_struct', artefactProps.TYPE_VALUE_RESULT,
                                             artefactProps.FORMAT_VALUE_DCM, fullPath)
            else:
              result = generateArtefactEntry(case, None, 0, 'BPLMR', artefactProps.TYPE_VALUE_RESULT,
                                           artefactProps.FORMAT_VALUE_DCM, fullPath)
    elif ext == ".fcsv":
        ps = fcsv.read_fcsv(fullPath)
        newPath = fullPath + '.txt'
        matchpoint.write_simple_pointset(newPath, ps)
        if not timepoint is None:
            #fraction directory
            result = generateArtefactEntry(case, None, timepoint, 'fxMR_points', artefactProps.TYPE_VALUE_RESULT,
                                             matchpoint.FORMAT_VALUE_MATCHPOINT_POINTSET, newPath)

        if pathParts[-1] == 'BPL_MR':
            result = generateArtefactEntry(case, None, timepoint, 'BPLMR_points', artefactProps.TYPE_VALUE_RESULT,
                                             matchpoint.FORMAT_VALUE_MATCHPOINT_POINTSET, newPath)
	

    return result
  
  
def generateArtefactList(root):
  crawler = DirectoryCrawler(root, mrgrtFileFunction, True)
  
  return crawler.getArtefacts()


if __name__ == "__main__":
  
  parser = argparse.ArgumentParser()
  parser.add_argument('root')
  parser.add_argument('output')
  cliargs, unknown = parser.parse_known_args()

  artefacts = generateArtefactList(cliargs.root)
  
  saveArtefactList(cliargs.output, artefacts)
