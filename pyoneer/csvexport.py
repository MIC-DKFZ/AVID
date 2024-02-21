# SPDX-FileCopyrightText: 2024, German Cancer Research Center (DKFZ), Division of Medical Image Computing (MIC)
#
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# or find it in LICENSE.txt.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import csv
from avid.common import osChecker
from pyoneer.htmlreport import getAllInstanceMeasurementValueKeys, getValueDisplayName, getMeasurementValueKeys, \
    getWorkflowModKeys


def _generateInstanceHeader(result, csvwriter):
    vkeys = getAllInstanceMeasurementValueKeys(result.instanceMeasurements)

    header = []
    if len(result.instanceMeasurements) > 0:
        eid = list(result.instanceMeasurements)[0]
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


def generateOptimizationCSV(result, csvFilePath):
    '''generates a CSV out of the optimization results (all candidates overview) and stores it as a csv file'''
    osChecker.checkAndCreateDir(os.path.split(csvFilePath)[0])
    with open(csvFilePath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')

        ms = result.candidates
        tableID = 1

        vkeys = getMeasurementValueKeys(ms, onlyWeigted=True)
        wmkeys = getWorkflowModKeys(ms)

        tablecontent = list()
        headers = ['Label', 'SV score']

        for wmkey in wmkeys:
            headers.append(wmkey)

        for vkey in vkeys:
            headers.append(getValueDisplayName(result,vkey))

        writer.writerow(headers)

        for m in ms:
            rowcontent = [m.label]
            rowcontent.append(m.svMeasure)

            for wmkey in wmkeys:
                rowcontent.append(m.workflowModifier[wmkey])

            for vkey in vkeys:
                try:
                    rowcontent.append(m.measurements[vkey])
                except:
                    rowcontent.append('N/A')

            writer.writerow(rowcontent)
