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

import argparse
import os

from pyoneer.evaluationResult import writeEvaluationResult, writeOptimizationResult
from pyoneer.optimization.strategy import detectOptimizationStrategies


def main():

  mainDesc = "Avid workflow optimization tool."
  parser = argparse.ArgumentParser(description = mainDesc)

  parser.add_argument('optimizationFile', help = "File specifying the optimization strategy (and evaluation strategy that should be used.")
  parser.add_argument('resultPath', help = "Path to the file where the optimization result should be stored to.")
  parser.add_argument('--artefacts', '-a', help = 'Specifies the artefact file that should be used to make the evaluations.')
  parser.add_argument('--evaluation', '-e', help = 'File specifying the evaluation strategy that should be used. Optional, needed if no evaluation strategy is specified in optimizationFile. Overwrites the strategy in optimizationFile.')
  parser.add_argument('--workflow', '-w', help = 'Specifies the workflow file that should be used to make the evaluations.')
  parser.add_argument('--sessionPath', '-s', help = "It defines the root directory where all the evaluation data is stored (temporarily). If not set it is <resultPath>/session")
  parser.add_argument('--name', '-n', help = 'Name of the session result folder in the rootpath defined by sessionPath. If not set it is the name of the used evaluation strategy".')
  parser.add_argument('--expandPaths','-x', help = 'Indicates if relative artefact path should be expanded when loading the data.')
  parser.add_argument('--debug', '-d', action='store_true', help = 'Indicates that the session should also log debug information (Therefore the log is more verbose).')
  parser.add_argument('--keepArtefacts', '-k', action='store_true', help = 'Indicates that the artefacts of the evaluation sessions should be kept and not be removed.')

  args_dict = vars(parser.parse_args())

  optStratClasses = detectOptimizationStrategies(args_dict['optimizationFile'])
  resultPath = args_dict['resultPath']
  sessionPath = args_dict['sessionPath']
  artefactPath = None
  if 'artefacts' in args_dict:
    artefactPath = args_dict['artefacts']

  workflowPath = None
  if 'workflow' in args_dict:
    workflowPath = args_dict['workflow']

  label = None
  if 'name' in args_dict:
    label = args_dict['name']

  evalStratFile = args_dict['optimizationFile']
  if 'evaluation' in args_dict:
    evalStratFile = args_dict['evaluation']

  if sessionPath is None:
    sessionPath = os.path.join(resultPath, 'session')

  for stratClass in optStratClasses:
    strat = stratClass(evalStratFile, sessionPath)
    result = strat.optimize(workflowPath,artefactPath, label=label)
    writeOptimizationResult(resultPath, result)

if __name__ == "__main__":
  main()