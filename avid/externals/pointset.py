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
class PointRepresentation(object):
    '''Simple representations for points in avid. Most generic to be able to swallow all kinds of input format
     (e.g. itk, mitk point sets, slicer fcsv). As a policy points in this representation should be stored in a
     LPS coordinate system (like DICOM or ITK).'''
    def __init__(self, x = 0, y = 0, z = 0, label = None, **args):
        self.x = x
        self.y = y
        self.z = z
        self.label = None