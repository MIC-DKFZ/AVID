#===================================================================
#
#The Medical Imaging Interaction Toolkit (MITK)
#
#Copyright (c) German Cancer Research Center,
#Division of Medical and Biological Informatics.
#All rights reserved.
#
#This software is distributed WITHOUT ANY WARRANTY; without
#even the implied warranty of MERCHANTABILITY or FITNESS FOR
#A PARTICULAR PURPOSE.
#
#See LICENSE.txt or http://www.mitk.org for details.
#
#===================================================================

import argparse
import os
import imp
import inspect
from ngeo.eval import EvaluationStrategy


def main():
  from ngeo.eval.evaluationResult import saveEvaluationResult

  mainDesc = "Avid workflow evaluation tool."
  parser = argparse.ArgumentParser(description = mainDesc)

  parser.add_argument('evaluation', help = "File specifing the evaluation strategy.")
  parser.add_argument('resultPath', help = "Path where the evaluation result should be stored to.")
  parser.add_argument('--artefacts', help = 'Specifies the artefact file that should be used to make the evaluations.')
  parser.add_argument('--workflow', help = 'Specifies the workflow file that should be used to make the evaluations.')
  parser.add_argument('--sessionPath', help = "It defines the root location where all the evaluation data is stored (temporarily).")
  parser.add_argument('--name', help = 'Name of the session result folder in the rootpath defined by sessionPath. If not set it will be "<sessionFile name>_session".')
  parser.add_argument('--expandPaths', help = 'Indicates if relative artefact path should be expanded when loading the data.')
  parser.add_argument('--debug', action='store_true', help = 'Indicates that the session should also log debug information (Therefore the log is more verbose).')
  parser.add_argument('--keepArtefacts', action='store_true', help = 'Indicates that the artefacts of the evaluation sessions should be stored and not be removed.')

  args_dict = vars(parser.parse_args())

  stratClasses = getEvaluationStrategies(args_dict['evaluation'])
  
  for stratClass in stratClasses:
    result = stratClass(args_dict['sessionPath'], args_dict['keepArtefacts']).evaluate('foo','bar')
    savePath = args_dict['sessionPath']
    saveEvaluationResult(savePath, result)


def predicateEvaluationStrategy(member):
  return inspect.isclass(member) and issubclass(member, EvaluationStrategy) and not member.__module__ == "ngeo.eval"

def getEvaluationStrategies(relevantFiles):
  '''searches for all EvaluationStrategy derivates in the given files and passes
  back a list of the found class objects.'''
  
  result = list()
  
  stratModule = imp.load_source('candidate', relevantFiles)
    
  for member in inspect.getmembers(stratModule, predicateEvaluationStrategy):
    result.append(member[1])

  return result  
    

if __name__ == "__main__":
  main()