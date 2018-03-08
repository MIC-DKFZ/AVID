# AVID - pyoneer
# AVID based tool for algorithmic evaluation and optimization
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
from builtins import object
import os
import xml.etree.ElementTree as ElementTree
from pyoneer.evaluation import EvalInstanceDescriptor
from avid.common.artefact.fileHelper import indent

class MeasurementResult(object):
    '''Class represents the measurement results of a workflow session with a set
    of workflow modifiers.'''
    def __init__(self, measurements, instanceMeasurements, label=None,
                 workflowModifier=None, measureWeights=None):
        '''Init of a MeasurmentResult instance.
        @param label: label for the measurements (e.g. used to indicate the optimization
        candidates.
        @param measurements: Dictionary containing the overall measurements for the
        whole test set.
        @param instanceMeasurements: Result dictionary with measurements for each
        instance. The key of the dict is a EvalInstanceDescriptor instance,
        the value is dictionary of measurements of one instance.
        @param workflowModifier: Dictionary of the workflow modifier used for the evaluation.
        @param measureWeights: Dictionary of the weights used to calculate the single
        value measure and the weightes measures of the evaluation.
        '''
        self.measurements = measurements
        self.instanceMeasurements = instanceMeasurements
        self.label = label
        self.workflowModifier = workflowModifier
        if self.workflowModifier is None:
            self.workflowModifier = dict()
        self.measureWeights = measureWeights

    @property
    def svMeasure(self):
        '''Convinience property that computes the single value measure usgin the
           measurements and the measureWeights. If measureWeights is None a weight of 1 for
           all measurements is assumed. If measureWeights is defined, all measurements
           not explicitly weighted will have the weight 0.'''

        result = 0.0

        for valueName in self.measurements:
            weight = 0.0
            if self.measureWeights is None:
                weight = 1.0
            else:
                try:
                    weight = self.measureWeights[valueName]
                except:
                    pass

            try:
                result = result + weight * self.measurements[valueName]
            except TypeError:
                pass  # if we cannot weight and add an measurment (because it is None), we just ignore it.

        return result

    @property
    def measurements_weighted(self):
        '''Convinience property that returns the measurment dictionary but with weighted results. It uses the
           measureWeights. If measureWeights is None a weight of 1 for
           all measurements is assumed. If measureWeights is defined, all measurements
           not explicitly weighted will have the weight 0.'''

        result = dict()

        for valueName in self.measurements:
            weight = 0.0
            if self.measureWeights is None:
                weight = 1.0
            else:
                try:
                    weight = self.measureWeights[valueName]
                except:
                    pass

            try:
                result[valueName] = weight * self.measurements[valueName]
            except TypeError:
                result[
                    valueName] = None  # if we cannot weight an measurment (because it is None), we just add it as None.

        return result

    def __eq__(self, other):
        if not self.measureWeights == other.measureWeights:
            return False
        if not self.instanceMeasurements == other.instanceMeasurements:
            return False
        if not self.measurements == other.measurements:
            return False
        if not self.workflowModifier == other.workflowModifier:
            return False
        if not self.label == other.label:
            return False

        return True

class ResultBase(object):
    '''Base class for representing evaluation or optimization results of an workflow.'''
    def __init__(self, name='unknown_evaluation',
                 workflowFile='', artefactFile='', valueNames=None, valueDescriptions=None):
        '''Init of a ResultBase instance.
        @param name: Name/lable of this evaluation.
        @param workflowFile: Path to the workflow script that was evaluated.
        @param artefactFile: Path to the artefact file that used to evaluated the workflow.
        @param valueNames: Dictionary of the display names of used measurements.
        @param valueDescriptions: Dictionary of the descriptions of used measurements.
        '''
        self.name = name
        self.workflowFile = workflowFile
        self.artefactFile = artefactFile
        self.valueNames = valueNames
        if self.valueNames is None:
            self.valueNames = dict()
        self.valueDescriptions = valueDescriptions
        if self.valueDescriptions is None:
            self.valueDescriptions = dict()

class EvaluationResult(ResultBase, MeasurementResult):
    '''Class that represents the results of an evaluation or optimization of an workflow.'''
    def __init__(self, measurements, instanceMeasurements,
                 workflowModifier=None, measureWeights=None, name='unknown_evaluation',
                 workflowFile='', artefactFile='', valueNames=None, valueDescriptions=None):
        '''Init of a EvaluationResult instance.
        @param measurements: Dictionary containing the overall measurements for the
        whole test set.
        @param instanceMeasurements: Result dictionary with measurements for each
        instance. The key of the dict is a EvalInstanceDescriptor instance,
        the value is dictionary of measurements of one instance.
        @param workflowModifier: Dictionary of the workflow modifier used for the evaluation.
        @param measureWeights: Dictionary of the weights used to calculate the single
        @param name: Name/lable of this evaluation.
        @param workflowFile: Path to the workflow script that was evaluated.
        @param artefactFile: Path to the artefact file that used to evaluated the workflow.
        @param valueNames: Dictionary of the display names of used measurements.
        @param valueDescriptions: Dictionary of the descriptions of used measurements.
        '''
        ResultBase.__init__(self, name=name, workflowFile=workflowFile,artefactFile=artefactFile,valueNames=valueNames,
                            valueDescriptions=valueDescriptions)
        MeasurementResult.__init__(self, measurements=measurements, instanceMeasurements=instanceMeasurements,
                                   workflowModifier=workflowModifier, measureWeights=measureWeights)


class OptimizationResult(ResultBase):
    '''Class that represents the results of an evaluation or optimization of an workflow.'''
    def __init__(self, best = None, candidates = None, name='unknown_evaluation',
                 workflowFile='', artefactFile='', valueNames=None, valueDescriptions=None):
        '''Init of a OptimizationResult instance.
        @param best List of best candidates indicated by the optimization
        @param list of all candidates evaluated in the optimization
        @param candidateResults: List of of results of evaluation candidates.
        @param name: Name/lable of this evaluation.
        @param workflowFile: Path to the workflow script that was evaluated.
        @param artefactFile: Path to the artefact file that used to evaluated the workflow.
        @param valueNames: Dictionary of the display names of used measurements.
        @param valueDescriptions: Dictionary of the descriptions of used measurements.
        '''
        ResultBase.__init__(self, name=name, workflowFile=workflowFile,artefactFile=artefactFile,valueNames=valueNames,
                            valueDescriptions=valueDescriptions)
        self.best = best
        if self.best is None:
            self.best = list()

        self.candidates = candidates
        if self.candidates is None:
            self.candidates = list()

    def append(self, evalResult, label = None, asBest = False):
        '''This method adds the measuremnts result to the optimization result.
        @param evalResult a EvaluatoinResult or MeasurementResult instance
        @param label label for the appended candidate. If None ot will use the label or name property of evalResult
        @asBest Indicates if it should be added as candidate (False) or as best element (True).
        '''

        mResult = MeasurementResult(evalResult.measurements.copy(), evalResult.instanceMeasurements.copy(),
                                    workflowModifier=evalResult.workflowModifier.copy(), measureWeights=evalResult.measureWeights.copy())
        if label is not None:
            mResult.label = label
        elif hasattr(evalResult, 'label') and evalResult.label is not None:
            mResult.label = evalResult.label
        elif hasattr(evalResult, 'name') and evalResult.name is not None:
            mResult.label = evalResult.name

        if asBest:
            self.best.append(mResult)
        else:
            self.candidates.append(mResult)

        if hasattr(evalResult, 'valueNames'):
            self.valueNames.update(evalResult.valueNames)
        if hasattr(evalResult, 'valueDescriptions'):
            self.valueDescriptions.update(evalResult.valueDescriptions)



XML_NAMESPACE = "http://www.dkfz.de/en/sidt/avid"
XML_NAMESPACE_DICT = {"avid": XML_NAMESPACE}
CURRENT_XML_VERSION = "1.0"

XML_ATTR_VERSION = "version"
XML_ATTR_KEY = "key"
XML_ATTR_LABEL = "label"
XML_EVALUATION_RESULT = "avid:evaluation_result"
XML_OPTIMIZATION_RESULT = "avid:optimization_result"
XML_NAME = "avid:name"
XML_WORKFLOWFILE = "avid:workflow_file"
XML_ARTEFACTFILE = "avid:artefact_file"
XML_BEST = "avid:best"
XML_CANDIDATES = "avid:candidates"
XML_CANDIDATE = "avid:candidate"
XML_SV_MEASUREMENT = "avid:sv_measurement"
XML_MEASURE_WEIGHTS = "avid:measure_weights"
XML_MEASURE_WEIGHT = "avid:measure_weight"
XML_WORKFLOW_MODS = "avid:workflow_modifiers"
XML_WORKFLOW_MOD = "avid:modifier"
XML_WORKFLOWFILE = "avid:workflow_file"
XML_MEASUREMENTS = "avid:measurements"
XML_MEASUREMENT = "avid:measurement"
XML_INSTANCES = "avid:measurement_instances"
XML_INSTANCE = "avid:measurement_instance"
XML_INSTANCE_DESCRIPTOR = "avid:instance_descriptor"
XML_INSTANCE_ID = "avid:id"
XML_DEF_VALUE = "avid:defining_value"
XML_MEASUREMENTS_INFO = "avid:measurements_info"
XML_INFO = "avid:info"
XML_VALUE_NAME = "avid:value_name"
XML_VALUE_DESC = "avid:value_description"
XML_VALUE = "avid:value"


def _initMeasurementResult(result, xmlNode):
    '''Init measurementResult with the information of a passed xmlNode.
    @param xmlNode: Node that represents a MeasurmentResult.
    '''

    try:
        result.label = xmlNode.attrib[XML_ATTR_LABEL]
    except:
        pass

    result.workflowModifier = {}
    for modNode in xmlNode.findall(XML_WORKFLOW_MODS + '/' + XML_WORKFLOW_MOD, XML_NAMESPACE_DICT):
        try:
            result.workflowModifier[modNode.attrib[XML_ATTR_KEY]] = modNode.text
        except:
            raise ValueError('XML has an invalid workflow modifier.')

    result.measureWeights = {}
    for wNode in xmlNode.findall(XML_MEASURE_WEIGHTS + '/' + XML_MEASURE_WEIGHT, XML_NAMESPACE_DICT):
        try:
            result.measureWeights[wNode.attrib[XML_ATTR_KEY]] = float(wNode.text)
        except:
            raise ValueError('XML has an invalid measurement weight.')

    for mNode in xmlNode.findall(XML_MEASUREMENTS + '/' + XML_MEASUREMENT, XML_NAMESPACE_DICT):
        try:
            result.measurements[mNode.attrib[XML_ATTR_KEY]] = float(mNode.text)
        except:
            if mNode.text is None:
                result.measurements[mNode.attrib[XML_ATTR_KEY]] = None
            else:
                raise ValueError('XML has an invalid measurement.')

    for iNode in xmlNode.findall(XML_INSTANCES + '/' + XML_INSTANCE, XML_NAMESPACE_DICT):
        defValues = dict()
        for dNode in iNode.findall(XML_INSTANCE_DESCRIPTOR + '/' + XML_DEF_VALUE, XML_NAMESPACE_DICT):
            try:
                defValues[dNode.attrib[XML_ATTR_KEY]] = dNode.text
            except:
                raise ValueError('XML has an invalid instance descriptor element')
        ID = None
        node = iNode.find(XML_INSTANCE_ID, XML_NAMESPACE_DICT)
        try:
            ID = node.text
        except:
            pass

        desc = EvalInstanceDescriptor(defValues, ID=ID)

        mNodes = iNode.findall(XML_MEASUREMENTS + '/' + XML_MEASUREMENT, XML_NAMESPACE_DICT)
        if len(mNodes)>0:
            measures = dict()
            for mNode in iNode.findall(XML_MEASUREMENTS + '/' + XML_MEASUREMENT, XML_NAMESPACE_DICT):
                vNodes = mNode.findall(XML_VALUE, XML_NAMESPACE_DICT)
                if len(vNodes) > 0:
                    values = list()
                    for vNode in vNodes:
                        try:
                            values.append(float(vNode.text))
                        except:
                            raise ValueError('XML has an invalid instance measurement list value.')
                    measures[mNode.attrib[XML_ATTR_KEY]] = values
                else:
                    try:
                        measures[mNode.attrib[XML_ATTR_KEY]] = float(mNode.text)
                    except:
                        if len(mNode.text) == 0:
                            measures[mNode.attrib[XML_ATTR_KEY]] = None
                        else:
                            raise ValueError('XML has an invalid instance measurement value.')

            result.instanceMeasurements[desc] = measures
        else:
            result.instanceMeasurements[desc] = None

def _initResultBase(base, xmlNode):
    '''Loads a evaluation result from an xml file.
    @param filePath Path where the evaluation result file is located.
    '''

    node = xmlNode.find(XML_NAME, namespaces=XML_NAMESPACE_DICT)
    try:
        base.name = node.text
    except:
        raise ValueError('XML has no valid name element')

    node = xmlNode.find(XML_WORKFLOWFILE, XML_NAMESPACE_DICT)
    try:
        base.workflowFile = node.text
    except:
        raise ValueError('XML has no valid workflow file element')

    node = xmlNode.find(XML_ARTEFACTFILE, XML_NAMESPACE_DICT)
    try:
        base.artefactFile = node.text
    except:
        raise ValueError('XML has no valid artefact file element')

    base.valueNames = dict()
    base.valueDescriptions = dict()
    for iNode in xmlNode.findall(XML_MEASUREMENTS_INFO + '/' + XML_INFO, XML_NAMESPACE_DICT):
        node = iNode.find(XML_VALUE_NAME, XML_NAMESPACE_DICT)
        try:
            base.valueNames[iNode.attrib[XML_ATTR_KEY]] = node.text
        except:
            pass
        node = iNode.find(XML_VALUE_DESC, XML_NAMESPACE_DICT)
        try:
            base.valueDescriptions[iNode.attrib[XML_ATTR_KEY]] = node.text
        except:
            pass

def readEvaluationResult(filePath):
    '''Loads a evaluation result from an xml file.
    @param filePath Path where the evaluation result file is located.
    '''
    result = EvaluationResult(dict(), dict())

    if not os.path.isfile(filePath):
        raise ValueError("Cannot load evaluation result from file. File does not exist. File path: " + str(filePath))

    tree = ElementTree.parse(filePath)
    root = tree.getroot()

    if root.tag != "{" + XML_NAMESPACE + "}evaluation_result":
        raise ValueError("XML has not the correct root element. Must be 'evaluation_result', but is: " + root.tag)

    _initResultBase(result,root)
    _initMeasurementResult(result,root)

    return result

def readOptimizationResult(filePath):
    '''Loads a optimization result from an xml file.
    @param filePath Path where the optimization result file is located.
    '''
    result = OptimizationResult()

    if not os.path.isfile(filePath):
        raise ValueError("Cannot load evaluation result from file. File does not exist. File path: " + str(filePath))

    tree = ElementTree.parse(filePath)
    root = tree.getroot()

    if root.tag != "{" + XML_NAMESPACE + "}optimization_result":
        raise ValueError("XML has not the correct root element. Must be 'optimization_result', but is: {}".format(root.tag))

    _initResultBase(result,root)

    for candidateNode in root.findall(XML_CANDIDATES+'/'+XML_CANDIDATE, XML_NAMESPACE_DICT):
        mResult = MeasurementResult({},{})
        _initMeasurementResult(mResult, candidateNode)
        result.append(mResult)

    for candidateNode in root.findall(XML_BEST+'/'+XML_CANDIDATE, XML_NAMESPACE_DICT):
        mResult = MeasurementResult({},{})
        _initMeasurementResult(mResult, candidateNode)
        result.append(mResult,asBest=True)

    return result

def xml_indent(elem, level=0):
    '''
    copy and paste from http://effbot.org/zone/element-lib.htm#prettyprint
    it basically walks your tree and adds spaces and newlines so the tree is
    printed in a nice way
    '''
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            xml_indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def _writeMeasurmentResult(result, builder):
    '''Helper function that writes an MeasurmentResult based instance "into" the builder'''
    builder.start(XML_WORKFLOW_MODS, {})
    for mID in result.workflowModifier:
        builder.start(XML_WORKFLOW_MOD, {XML_ATTR_KEY: mID})
        builder.data(str(result.workflowModifier[mID]))
        builder.end(XML_WORKFLOW_MOD)
    builder.end(XML_WORKFLOW_MODS)

    builder.start(XML_SV_MEASUREMENT, {})
    builder.data(str(result.svMeasure))
    builder.end(XML_SV_MEASUREMENT)

    builder.start(XML_MEASURE_WEIGHTS, {})
    try:
        for mID in result.measureWeights:
            builder.start(XML_MEASURE_WEIGHT, {XML_ATTR_KEY: mID})
            builder.data(str(result.measureWeights[mID]))
            builder.end(XML_MEASURE_WEIGHT)
    except:
        pass
    builder.end(XML_MEASURE_WEIGHTS)

    builder.start(XML_MEASUREMENTS, {})
    for mID in result.measurements:
        builder.start(XML_MEASUREMENT, {XML_ATTR_KEY: mID})
        if not result.measurements[mID] is None:
            builder.data(str(result.measurements[mID]))
        else:
            builder.data('')
        builder.end(XML_MEASUREMENT)
    builder.end(XML_MEASUREMENTS)

    builder.start(XML_INSTANCES, {})
    for desc in result.instanceMeasurements:
        builder.start(XML_INSTANCE, {})

        builder.start(XML_INSTANCE_DESCRIPTOR, {})
        builder.start(XML_INSTANCE_ID, {})
        builder.data(str(desc.ID))
        builder.end(XML_INSTANCE_ID)

        for defValue in desc._definingValues:
            builder.start(XML_DEF_VALUE, {XML_ATTR_KEY: defValue})
            builder.data(str(desc._definingValues[defValue]))
            builder.end(XML_DEF_VALUE)
        builder.end(XML_INSTANCE_DESCRIPTOR)

        builder.start(XML_MEASUREMENTS, {})
        try:
            for mID in result.instanceMeasurements[desc]:
                builder.start(XML_MEASUREMENT, {XML_ATTR_KEY: mID})
                if not result.instanceMeasurements[desc][mID] is None:
                    try:
                        for value in result.instanceMeasurements[desc][mID]:
                            builder.start(XML_VALUE, {})
                            builder.data(str(value))
                            builder.end(XML_VALUE)
                    except:
                        builder.data(str(result.instanceMeasurements[desc][mID]))
                else:
                    builder.data('')
                builder.end(XML_MEASUREMENT)
        except:
            pass
        builder.end(XML_MEASUREMENTS)

        builder.end(XML_INSTANCE)

    builder.end(XML_INSTANCES)


def _writeResultBase(result, builder):
    '''Helper function that writes an ResultBase based instance "into" the builder'''
    builder.start(XML_NAME, {})
    builder.data(str(result.name))
    builder.end(XML_NAME)

    builder.start(XML_WORKFLOWFILE, {})
    builder.data(str(result.workflowFile))
    builder.end(XML_WORKFLOWFILE)

    builder.start(XML_ARTEFACTFILE, {})
    builder.data(str(result.artefactFile))
    builder.end(XML_ARTEFACTFILE)

    builder.start(XML_MEASUREMENTS_INFO, {})
    keys = set(list(result.valueNames.keys()) + list(result.valueDescriptions.keys()))

    for key in keys:
        builder.start(XML_INFO, {XML_ATTR_KEY: key})

        if key in result.valueNames:
            builder.start(XML_VALUE_NAME, {})
            builder.data(str(result.valueNames[key]))
            builder.end(XML_VALUE_NAME)

        if key in result.valueDescriptions:
            builder.start(XML_VALUE_DESC, {})
            builder.data(str(result.valueDescriptions[key]))
            builder.end(XML_VALUE_DESC)

        builder.end(XML_INFO)

    builder.end(XML_MEASUREMENTS_INFO)


def writeEvaluationResult(filePath, evalResult):
    builder = ElementTree.TreeBuilder()

    builder.start(XML_EVALUATION_RESULT, {XML_ATTR_VERSION: CURRENT_XML_VERSION, "xmlns:avid": XML_NAMESPACE})

    _writeResultBase(evalResult, builder)
    _writeMeasurmentResult(evalResult, builder)

    builder.end(XML_EVALUATION_RESULT)

    root = builder.close()
    tree = ElementTree.ElementTree(root)
    indent(root)

    try:
        os.makedirs(os.path.split(filePath)[0])
    except:
        pass

    if os.path.isfile(filePath):
        os.remove(filePath)

    tree.write(filePath, xml_declaration=True)


def writeOptimizationResult(filePath, result):
    builder = ElementTree.TreeBuilder()

    builder.start(XML_OPTIMIZATION_RESULT, {XML_ATTR_VERSION: CURRENT_XML_VERSION, "xmlns:avid": XML_NAMESPACE})

    _writeResultBase(result, builder)

    builder.start(XML_BEST, {})
    for candidate in result.best:
        candidate_dict = {}
        if candidate.label is not None:
            candidate_dict[XML_ATTR_LABEL] = candidate.label
        builder.start(XML_CANDIDATE, candidate_dict)
        _writeMeasurmentResult(candidate, builder)
        builder.end(XML_CANDIDATE)
    builder.end(XML_BEST)

    builder.start(XML_CANDIDATES, {})
    for candidate in result.candidates:
        candidate_dict = {}
        if candidate.label is not None:
            candidate_dict[XML_ATTR_LABEL] = candidate.label
        builder.start(XML_CANDIDATE, candidate_dict)
        _writeMeasurmentResult(candidate, builder)
        builder.end(XML_CANDIDATE)
    builder.end(XML_CANDIDATES)

    builder.end(XML_OPTIMIZATION_RESULT)

    root = builder.close()
    tree = ElementTree.ElementTree(root)
    indent(root)

    try:
        os.makedirs(os.path.split(filePath)[0])
    except:
        pass

    if os.path.isfile(filePath):
        os.remove(filePath)

    tree.write(filePath, xml_declaration=True)
