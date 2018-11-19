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
import argparse
import logging
import os

import sys

from pyoneer import htmlreport
from pyoneer import csvexport
from pyoneer.evaluation import detectEvaluationStrategies
from pyoneer.evaluationResult import writeEvaluationResult, writeOptimizationResult, readOptimizationResult, \
    readEvaluationResult
from pyoneer.optimization.strategy import detectOptimizationStrategies
import webbrowser

def doEvaluation(stratFile, resultPath, workflowPath, artefactPath, label, sessionPath, args_dict):
    stratClasses = detectEvaluationStrategies(stratFile)

    workflowMod = None
    if args_dict['modifier'] is not None:
        workflowMod = dict()
        for mod in args_dict['modifier']:
            workflowMod[mod[0]] = mod[1]

    for stratClass in stratClasses:
        result = stratClass(sessionPath, not args_dict['keepArtefacts']).evaluate(workflowFile=workflowPath,
                                                                                  artefactFile=artefactPath, label=label,
                                                                                  workflowModifier= workflowMod)
        writeEvaluationResult(resultPath, result)

        if args_dict['report'] is not None:
            reportPath = resultPath + os.extsep + 'html'
            if len(args_dict['report'])>0:
                reportPath = args_dict['report']

            report = htmlreport.generateEvaluationReport(result)

            with open(reportPath, 'w') as fileHandle:
                fileHandle.write(report)

            if args_dict['noDisplay'] is not True:
                webbrowser.open('file:///'+reportPath)

        if args_dict['csv'] is not None:
            csvPath = resultPath + os.extsep + 'csv'
            if len(args_dict['csv'])>0:
                csvPath = args_dict['csv']

            csvexport.generateEvaluationCSV(result, csvPath)


class InterimReporter(object):
    def __init__(self, resultPath, reportPath = None):
        self._resultPath = resultPath
        self._reportPath = reportPath

    def __call__(self, *args, **kwargs):
        writeOptimizationResult(self._resultPath, args[1])

        if self._reportPath is not None:
            report = htmlreport.generateOptimizationReport(args[1])

            with open(self._reportPath, 'w') as fileHandle:
                fileHandle.write(report)

def doOptimization(stratFile, resultPath, workflowPath, artefactPath, label, sessionPath, evalStratFile, args_dict):

    optStratClasses = detectOptimizationStrategies(stratFile)

    reportPath = None
    if args_dict['report'] is not None:
        reportPath = resultPath + os.extsep + 'html'
        if len(args_dict['report']) > 0:
            reportPath = args_dict['report']

    workflowMod = None
    if args_dict['modifier'] is not None:
        workflowMod = dict()
        for mod in args_dict['modifier']:
            workflowMod[mod[0]] = mod[1]

    for stratClass in optStratClasses:
        reportCallBack = None
        if args_dict['interim'] is not None:
            reportCallBack = InterimReporter(resultPath, reportPath)

        strat = stratClass(evalStratFile, sessionPath, reportCallBack)
        result = strat.optimize(workflowPath,artefactPath, label=label, userWorkflowModifier=workflowMod)
        writeOptimizationResult(resultPath, result)

        if args_dict['report'] is not None:
            report = htmlreport.generateOptimizationReport(result)

            with open(reportPath, 'w') as fileHandle:
                fileHandle.write(report)

            if args_dict['noDisplay'] is not True:
                webbrowser.open('file:///'+reportPath)


def doReport(inputFilePath, resultPath, args_dict):

    if args_dict['report'] is not None:
        logging.warn("Report flag is ignored when using the report command.")

    validReport = False

    try:
        result = readOptimizationResult(inputFilePath)
        report = htmlreport.generateOptimizationReport(result)

        with open(resultPath, 'w') as fileHandle:
            fileHandle.write(report)

        validReport = True
    except:
        try:
            result = readEvaluationResult(inputFilePath)

            csvPath = resultPath
            csvOnly = False

            if args_dict['csv'] is not None:
                if len(args_dict['csv'])>0:
                    csvPath = args_dict['csv']
                else:
                    csvOnly = True

                csvexport.generateEvaluationCSV(result, csvPath)

            if not csvOnly:
                report = htmlreport.generateEvaluationReport(result)
                with open(resultPath, 'w') as fileHandle:
                    fileHandle.write(report)
                validReport = True

        except:
            logging.error('Cannot convert result file to report. Seems to be no valid evaluation or optimization result file. Invalid file: "%s".',
                         inputFilePath)

    if args_dict['noDisplay'] is not True and validReport is True:
        webbrowser.open('file:///' + resultPath)


def main():

    mainDesc = "Avid Pyoneer - workflow optimization and evaluation tool."
    parser = argparse.ArgumentParser(description = mainDesc)

    parser.add_argument('command', help = "Specifies the type of work pyoneer should do.", choices = ['evaluate', 'optimize', 'report'])
    parser.add_argument('inputFile', help = "File specifying input for pyoneer. For commands 'evaluate' and 'optimize' it specifies the strategies (optimazation and/or evaluation strategy that should be used.). For 'report' it is the path to the result file that should be converted into a html report.")
    parser.add_argument('resultPath', help = "Path to the file where the result should be stored to.")
    parser.add_argument('--artefacts', '-a', help = 'Specifies the artefact file that should be used to make the evaluations.')
    parser.add_argument('--evaluation', '-e', help = 'File specifying the evaluation strategy that should be used. Optional, needed if no evaluation strategy is specified in strategyFile. Overwrites the strategy in strategyFile.')
    parser.add_argument('--workflow', '-w', help = 'Specifies the workflow file that should be used to make the evaluations or that should be optimized.')
    parser.add_argument('--sessionPath', '-s', help = "It defines the root directory where all the evaluation data is stored (temporarily). If not set it is <resultPath>/session")
    parser.add_argument('--name', '-n', help = 'Name of the session result folder in the rootpath defined by sessionPath. If not set it is the name of the used evaluation strategy".')
    parser.add_argument('--expandPaths','-x', help = 'Indicates if relative artefact path should be expanded when loading the data. (Only relevant for evaluations)')
    parser.add_argument('--debug', '-d', action='store_true', help = 'Indicates that the session should also log debug information (Therefore the log is more verbose).')
    parser.add_argument('--keepArtefacts', '-k', action='store_true', help = 'Indicates that the artefacts of the evaluation sessions should be kept and not be removed. (Only relevant for evaluations)')
    parser.add_argument('--report', '-r', nargs='?', const='', default=None, help = 'Generates and displays an html report out of the result. If no explicit path is specified it will use the result path with an added html extension.')
    parser.add_argument('--noDisplay', '-y', action='store_true', help = 'Indicates that generated html report should just be stored and not displayed (e.g. when AVID pyoneer runs on a server terminal).')
    parser.add_argument('--interim', '-i', action='store_true', help = 'Indicates already interim results of the optimization process should be reported. Meaning results will be stored also after each candidate evaluation.')
    parser.add_argument('--modifier', '-m', action='append', nargs=2, metavar=('key', 'value'), help='Allows to pass workflow modifier to the evaluation when using "avidpyoneer evalute" or "avidpyoneer optimize". The key is assumed to be the argument name (--<key>) and the value content will be forwarded to the workflow under evaluation.')
    parser.add_argument('--csv', '-c', nargs='?', const='', default=None, help = 'Generates a csv (comma seperated value) file out of the result. In case of evaluation it contains all instance results. In case of an optimiztion it containes the optimization process. You may use it with any action (evaluate, optimize, report). If no explicit path is specified it will use the result path with an added csv extension.')

    args_dict = vars(parser.parse_args())

    inputFile = args_dict['inputFile']
    resultPath = args_dict['resultPath']

    artefactPath = args_dict['artefacts']

    workflowPath = args_dict['workflow']

    label = args_dict['name']

    evalStratFile = args_dict['inputFile']
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
        if not os.path.exists(workflowPath):
            logging.fatal("Error. Cannot evaluate workflow. Specified workflow path does not exist. Invalid path: {}".format(workflowPath))
            return
        if not os.path.exists(artefactPath):
            logging.fatal("Error. Cannot evaluate workflow. Specified artefact path does not exist. Invalid path: {}".format(artefactPath))
            return
        doEvaluation(evalStratFile, resultPath, workflowPath, artefactPath, label, sessionPath, args_dict)
    elif args_dict['command'] == "optimize":
        if not os.path.exists(workflowPath):
            logging.fatal("Error. Cannot evaluate workflow. Specified workflow path does not exist. Invalid path: {}".format(workflowPath))
            return
        if not os.path.exists(artefactPath):
            logging.fatal("Error. Cannot evaluate workflow. Specified artefact path does not exist. Invalid path: {}".format(artefactPath))
            return
        doOptimization(inputFile, resultPath, workflowPath, artefactPath, label, sessionPath, evalStratFile, args_dict)
    elif args_dict['command'] == "report":
        doReport(inputFile, resultPath, args_dict)


if __name__ == "__main__":
  main()