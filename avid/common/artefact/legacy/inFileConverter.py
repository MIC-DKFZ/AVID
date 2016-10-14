__author__ = 'hentsch'

import avid.common.artefact.fileHelper as fileHelper
import argparse, sys

__this__ = sys.modules[__name__]

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--inFile')
parser.add_argument('-o', '--outFile')
args = parser.parse_args()

data = fileHelper.loadArtefactList_csv(args.inFile)
fileHelper.saveArtefactList_xml(args.outFile, data)