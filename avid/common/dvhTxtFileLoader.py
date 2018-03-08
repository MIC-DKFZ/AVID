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

from builtins import object
class DVHType(object):
    Cumulative = 1
    Differential = 2

class DVHContainer(object):
    ''' Simple dvh container for RTTB dvh files'''
    def __init__(self):
        ''''''
        self.dvhType = DVHType.Cumulative 
        self.deltaDose = 1.0
        self.deltaVolume = 1.0
        self.structureID = "unknown"
        self.doseID = "unknown"
        self.dvhData = []

def parseParameter(lineStr):
    ''' parses a given line for [Name]: [Value]. Splits at ':'. Returns a tuple.
    First element is the name string. Second element is value
    (with all leading spaces removed). If no value is defined an empty string
    will be returned.'''
    splitParts = lineStr.split(':')
    name = splitParts[0]
    value = ''

    if len(splitParts) > 1:
        value = splitParts[1].lstrip().rstrip()

    return [name, value]

def parseFile(fileName):
    ''' parse the passed input file and returns an instance of DVHContainer
     filled with the content.  May raise exception if file has no valid structure'''

    dvh = DVHContainer()

    with open(fileName,'r') as file:
        isDVHDataBlock = False
        for line in file:
            if not isDVHDataBlock:
                param = parseParameter(line)
                if param[0] == "DVH Type":
                    if param[1] == "CUMULATIVE":
                        dvh.dvhType = DVHType.Cumulative
                    else:
                        dvh.dvhType = DVHType.Differential
                elif param[0] == "DeltaD":
                    dvh.deltaDose = float(param[1])
                elif param[0] == "DeltaV":
                    dvh.deltaVolume = float(param[1])
                elif param[0] == "StructureID":
                    dvh.structureID = param[1]
                elif param[0] == "DoseID":
                    dvh.doseID = param[1]
                elif param[0] == "DVH Data":
                    isDVHDataBlock = True
            else:
                splitParts = line.split(',')

                if len(splitParts) < 2:
                    raise RuntimeError("DVH data part seems to be invalid. Data line has only one value")

                dvh.dvhData.append(float(splitParts[1]))
            
    return dvh

