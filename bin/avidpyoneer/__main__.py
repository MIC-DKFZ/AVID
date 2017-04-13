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
import logging
import os

import sys

from pyoneer.evaluation import detectEvaluationStrategies
from pyoneer.evaluationResult import writeEvaluationResult, writeOptimizationResult
from pyoneer.optimization.strategy import detectOptimizationStrategies

def doEvaluation(stratFile, resultPath, workflowPath, artefactPath, label, sessionPath, args_dict):
    stratClasses = detectEvaluationStrategies(stratFile)
    for stratClass in stratClasses:
        result = stratClass(sessionPath, args_dict['keepArtefacts']).evaluate(workflowFile=workflowPath,
                                                                              artefactFile=artefactPath, label=label)
        writeEvaluationResult(resultPath, result)


def doOptimization(stratFile, resultPath, workflowPath, artefactPath, label, sessionPath, evalStratFile, args_dict):

    optStratClasses = detectOptimizationStrategies(stratFile)

    for stratClass in optStratClasses:
        strat = stratClass(evalStratFile, sessionPath)
        result = strat.optimize(workflowPath,artefactPath, label=label)
        writeOptimizationResult(resultPath, result)


def main():

    mainDesc = "Avid Pyoneer - workflow optimization and evaluation tool."
    parser = argparse.ArgumentParser(description = mainDesc)

    parser.add_argument('command', help = "Specifies the type of work pyoneer should do.", choices = ['evaluate', 'optimize'])
    parser.add_argument('strategyFile', help = "File specifying the strategies (optimazation and/or evaluation strategy that should be used.)")
    parser.add_argument('resultPath', help = "Path to the file where the result should be stored to.")
    parser.add_argument('--artefacts', '-a', help = 'Specifies the artefact file that should be used to make the evaluations.')
    parser.add_argument('--evaluation', '-e', help = 'File specifying the evaluation strategy that should be used. Optional, needed if no evaluation strategy is specified in strategyFile. Overwrites the strategy in strategyFile.')
    parser.add_argument('--workflow', '-w', help = 'Specifies the workflow file that should be used to make the evaluations or that should be optimized.')
    parser.add_argument('--sessionPath', '-s', help = "It defines the root directory where all the evaluation data is stored (temporarily). If not set it is <resultPath>/session")
    parser.add_argument('--name', '-n', help = 'Name of the session result folder in the rootpath defined by sessionPath. If not set it is the name of the used evaluation strategy".')
    parser.add_argument('--expandPaths','-x', help = 'Indicates if relative artefact path should be expanded when loading the data. (Only relevant for evaluations)')
    parser.add_argument('--debug', '-d', action='store_true', help = 'Indicates that the session should also log debug information (Therefore the log is more verbose).')
    parser.add_argument('--keepArtefacts', '-k', action='store_true', help = 'Indicates that the artefacts of the evaluation sessions should be kept and not be removed. (Only relevant for evaluations)')

    args_dict = vars(parser.parse_args())

    stratFile = args_dict['strategyFile']
    resultPath = args_dict['resultPath']

    artefactPath = args_dict['artefacts']

    workflowPath = args_dict['workflow']

    label = args_dict['name']

    evalStratFile = args_dict['strategyFile']
    if args_dict['evaluation'] is not None:
        evalStratFile = args_dict['evaluation']

    sessionPath = args_dict['sessionPath']
    if sessionPath is None:
        sessionPath = resultPath+'_session'

    # logging setup
    logginglevel = logging.INFO
    if args_dict['debug']:
        logginglevel = logging.DEBUG

    resultDir = os.path.split(resultPath)[0]

    try:
        os.makedirs(resultDir)
    except:
        pass

    logging.basicConfig(filename=resultPath + ".log", filemode='w', level=logginglevel,
                        format='%(levelname)-8s %(asctime)s [MODULE] %(module)-20s [Message] %(message)s [Location] %(funcName)s in %(pathname)s %(lineno)d')
    rootlogger = logging.getLogger()

    stdoutlogstream = logging.StreamHandler(sys.stdout)
    stdoutlogstream.setLevel(logging.INFO)
    streamFormater = logging.Formatter('%(asctime)-8s [%(levelname)s] %(message)s')
    stdoutlogstream.setFormatter(streamFormater)
    rootlogger.addHandler(stdoutlogstream)

    #do the job
    if args_dict['command'] == "evaluate":
        doEvaluation(evalStratFile, resultPath, workflowPath, artefactPath, label, sessionPath, args_dict)
    elif args_dict['command'] == "optimize":
        doOptimization(stratFile, resultPath, workflowPath, artefactPath, label, sessionPath, evalStratFile, args_dict)


if __name__ == "__main__":
  main()