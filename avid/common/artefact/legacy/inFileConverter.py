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

import avid.common.artefact.fileHelper as fileHelper
import argparse, sys

__this__ = sys.modules[__name__]

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--inFile')
parser.add_argument('-o', '--outFile')
args = parser.parse_args()

data = fileHelper.loadArtefactList_csv(args.inFile)
fileHelper.saveArtefactList_xml(args.outFile, data)