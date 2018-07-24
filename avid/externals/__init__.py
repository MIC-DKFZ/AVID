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

import os
from avid.common.osChecker import checkAndCreateDir


def configureExternalFile(inFilePath, outFilePath, paramDict, paramEscape='@'):
    '''reads a given inFilePath configures/modifies it by the given parameter dictionary
    and stores the result at outFilePath.
    Configuration is done be searching for any key in the paramDict and replacing its
    occurence with the value associated with the key.
    @param paramEscape specifies how the keys are escaped in the input file. Default would be
     '@key1@'.'''
    with open(inFilePath, 'r') as ifile_handle:
        content = ifile_handle.read()

        for key in paramDict:
            symbol = paramEscape + str(key) + paramEscape
            content = content.replace(symbol, str(paramDict[key]))

        checkAndCreateDir(os.path.split(outFilePath)[0])
        with open(outFilePath, 'w') as ofile_handle:
            ofile_handle.write(content)
