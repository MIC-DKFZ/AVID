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

import logging
import os
import xml
import re

logger = logging.getLogger(__name__)

COMPARE_KEYS = ['MIN','AVE','MAX','MAE', 'MSE', 'DIF', 'NUM', 'RATIO']

def parseCompareResult(outputStr):
  '''Helper that parses the output of plastimatch compare into a dict.
  @param outputStr: String that contains the output of plastimatch compare
  @result Dictionary that containes the result values of the plastimatch call.
  Keys are (From the plastimatch documentation): 
  MIN      Minimum value of difference image
  AVE      Average value of difference image
  MAX      Maximum value of difference image
  MAE      Mean average value of difference image
  MSE      Mean squared difference between images
  DIF      Number of pixels with different intensities
  NUM      Total number of voxels in the difference image
  And additionally:
  RATIO    ratio between DIF and NUM
  '''
  result = dict()
  
  lines = outputStr.splitlines()
  
  for line in lines:
    items = filter(None, line.split())
    key = None
    for item in items:
      candidate = item.strip(' \t\n\r')
      if candidate in COMPARE_KEYS:
        key = candidate
      elif not key is None:
        result[key] = float(candidate)
        
  result['RATIO'] = result['DIF']/result['NUM']
  
  return result

DICE_KEYS = ['TP','TN','FN','FP','DICE','SE','SP',
             'Hausdorff distance','Avg average Hausdorff distance',
             'Max average Hausdorff distance','Percent (0.95) Hausdorff distance',
             'Hausdorff distance (boundary)','Avg average Hausdorff distance (boundary)',
             'Max average Hausdorff distance (boundary)','Percent (0.95) Hausdorff distance (boundary)']

def parseDiceResult(outputStr):
  '''Helper that parses the output of plastimatch dice into a dict.
  @param outputStr: String that contains the output of plastimatch compare
  @result Dictionary that containes the result values of the plastimatch call.
  Keys are:
  'TP','TN','FN','FP','DICE','SE','SP',
  'Hausdorff distance','Avg average Hausdorff distance',
  'Max average Hausdorff distance','Percent (0.95) Hausdorff distance',
  'Hausdorff distance (boundary)','Avg average Hausdorff distance (boundary)',
  'Max average Hausdorff distance (boundary)','Percent (0.95) Hausdorff distance (boundary)'
  '''
  result = dict()
  
  lines = outputStr.splitlines()
  for line in lines:
    try:
      items = filter(None, re.split(r'\s*[:,\=]\s*', line))
      if items[0] in DICE_KEYS:
        result[items[0]] = float(items[1])
    except:
      pass
    
  return result
