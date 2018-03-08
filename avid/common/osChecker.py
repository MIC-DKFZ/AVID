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
import errno
import platform

def checkAndCreateDir(completePath):
  """ generates a directory """
  try:
    os.makedirs(completePath)
  except OSError as exc:
    if exc.errno != errno.EEXIST:
      raise exc
    pass

def isWindows():
  """returns true if runs on a windows system"""
  return platform.system() == 'Windows'
