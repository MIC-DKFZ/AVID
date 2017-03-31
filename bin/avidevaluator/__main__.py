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
import imp
import inspect
import os

from pyoneer.evaluation import detectEvaluationStrategies


def main():
  from pyoneer.evaluationResult import saveEvaluationResult

  mainDesc = "Avid workflow evaluation tool."
  parser = argparse.ArgumentParser(description = mainDesc)

  parser.add_argument('evaluation', help = "File specifing the evaluation strategy.")
  parser.add_argument('resultPath', help = "Path where the evaluation result should be stored to.")
  parser.add_argument('--artefacts', help = 'Specifies the artefact file that should be used to make the evaluations.')
  parser.add_argument('--workflow', help = 'Specifies the workflow file that should be used to make the evaluations.')
  parser.add_argument('--sessionPath', help = "It defines the root directory where all the evaluation data is stored (temporarily). If not set it is <resultPath>/session")
  parser.add_argument('--label', help = 'Name of the session result folder in the rootpath defined by sessionPath. If not set it is the name of the used evaluation strategy".')
  parser.add_argument('--expandPaths', help = 'Indicates if relative artefact path should be expanded when loading the data.')
  parser.add_argument('--debug', action='store_true', help = 'Indicates that the session should also log debug information (Therefore the log is more verbose).')
  parser.add_argument('--keepArtefacts', action='store_true', help = 'Indicates that the artefacts of the evaluation sessions should be kept and not be removed.')

  args_dict = vars(parser.parse_args())

  stratClasses = detectEvaluationStrategies(args_dict['evaluation'])
  resultPath = args_dict['resultPath']
  sessionPath = args_dict['sessionPath']
  artefactPath = None
  if 'artefacts' in args_dict:
    artefactPath = args_dict['artefacts']

  workflowPath = None
  if 'workflow' in args_dict:
    workflowPath = args_dict['workflow']

  label = None
  if 'label' in args_dict:
    label = args_dict['label']

  if sessionPath is None:
    sessionPath = os.path.join(resultPath, 'session')

  for stratClass in stratClasses:
    result = stratClass(sessionPath, args_dict['keepArtefacts']).evaluate(workflowFile=workflowPath, artefactFile=artefactPath, label=label)
    saveEvaluationResult(resultPath, result)


if __name__ == "__main__":
  main()