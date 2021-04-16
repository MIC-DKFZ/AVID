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

from avid.splitter import BaseSplitter

class SingleSplitter(BaseSplitter):
    '''Splits the passed selection in single artefacts. So the resulting list of split selection will only contain one artefact each.'''
    def __init__(self):
        super().__init__()
        return

    def splitSelection(self, selection):
        splittedList = list()
        for item in selection:
            splittedList.append([item])

        return splittedList
