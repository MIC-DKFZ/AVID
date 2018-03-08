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

from builtins import str
def writeFileCustomized(templateFilename, targetFilename, replaceDict):
  inputFile = open(templateFilename, 'r')
  content = inputFile.read()
  inputFile.close()

  for key, value in replaceDict.items() :
    content = content.replace(key, str(value))

  outputFile = open(targetFilename, 'w')
  outputFile.write(content)
  outputFile.close()