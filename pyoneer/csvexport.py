# AVID - pyoneer
# AVID based tool for algorithmic evaluation and optimization
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

import os
import csv
from avid.common import osChecker
from pyoneer.htmlreport import getAllInstanceMeasurementValueKeys, getValueDisplayName


def _generateInstanceHeader(result, csvwriter):
    vkeys = getAllInstanceMeasurementValueKeys(result.instanceMeasurements)

    header = []
    if len(result.instanceMeasurements) > 0:
        eid = result.instanceMeasurements.keys()[0]
        for eidKey in sorted(eid.keys()):
            header.append(eidKey)

    for vkey in vkeys:
        header.append(getValueDisplayName(result,vkey))

    csvwriter.writerow(header)

def _generateInstanceContent(result, csvwriter):
    vkeys = getAllInstanceMeasurementValueKeys(result.instanceMeasurements)
    for imkey in result.instanceMeasurements:
        im = result.instanceMeasurements[imkey]

        content = []

        eidKeys = sorted(imkey.keys())
        for eidKey in eidKeys:
            content.append(imkey[eidKey])

        for vkey in vkeys:
            try:
                content.append(im[vkey])
            except:
                content.append('')

        csvwriter.writerow(content)

def generateEvaluationCSV(result, csvFilePath):
    '''generates a CSV out of the evaluation results (the instance measures) and stores it as a csv file'''
    osChecker.checkAndCreateDir(os.path.split(csvFilePath)[0])
    with open(csvFilePath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')

        _generateInstanceHeader(result, writer)
        _generateInstanceContent(result, writer)
