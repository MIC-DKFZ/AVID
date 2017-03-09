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

import csv
import os
from pointset import PointRepresentation

'''Formate type value. Indicating the artefact is stored as a MatchPoint simple point set file.'''
FORMAT_VALUE_SLICER_POINTSET = "3Dslicer_pointset"


def load_fcsv(filePath):
    '''Loads a point set stored in slicer fcsv format. The points stored in a list as PointRepresentation instances.
    While loaded the points are converted from RAS (slicer) to LPS (DICOM, itk).
    @param filePath Path where the fcsv file is located.
    '''
    points = list()

    if not os.path.isfile(filePath):
        raise ValueError( "Cannot load fcsv point set file. File does not exist. File path: " +str(filePath))

    with open(filePath, "rb") as csvfile:
        pointreader = csv.reader(csvfile, delimiter = ",")

        for row in pointreader:
            point = PointRepresentation(label = None)
            for no ,entry in enumerate(row):
                if no == 0:
                    point.label = entry
                elif no == 1:
                    try:
                        point.x = float(entry)
                    except:
                        ValueError("Cannot convert x element of point in fcsv point set. Invalid point #: {}; invalid value: {}".format(row, entry))
                elif no == 2:
                    try:
                        point.y = float(entry)
                    except:
                        ValueError("Cannot convert y element of point in fcsv point set. Invalid point #: {}; invalid value: {}".format(row, entry))
                elif no == 3:
                    try:
                        point.z = float(entry)
                    except:
                        ValueError("Cannot convert z element of point in fcsv point set. Invalid point #: {}; invalid value: {}".format(row, entry))

            #convert RAS (orientation of slicer) into LPS (orientation of DICOM, itk and avid)
            point.x = -1*point.x
            point.y = -1*point.y
            points.append(point)

    return points