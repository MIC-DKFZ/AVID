###AVIDHEADER

import os
import xml.etree.ElementTree as ElementTree
from ngeo.eval import EvalInstanceDescriptor
from avid.common.artefact.fileHelper import indent

class EvaluationResult (object):
  
  def __init__(self, measurements, instanceMeasurements, name = 'unknown_evaluation',
               workflowFile = '', artefactFile = '', workflowModifier = {},
               svWeights = None, valueNames = {}, valueDescriptions = {}):
    '''Init of a EvaluationResult instance.
    @param measurements: Dictionary containing the overall measurements for the
    whole test set.  
    @param instanceMeasurements: Result dictionary with measurements for each
    instance. The key of the dict is a EvalInstanceDescriptor instance,
    the value is dictionary of measurements of one instance.  
    @param name: Name/lable of this evaluation.  
    @param workflowFile: Path to the workflow script that was evaluated.  
    @param artefactFile: Path to the artefact file that used to evaluated the workflow.  
    @param workflowModifier: Dictionary of the workflow modifier used for the evaluation.
    @param svWeights: Dictionary of the weights used to calculate the single
    value measure of the evaluation.
    @param valueNames: Dictionary of the display names of used measurements.  
    @param valueDescriptions: Dictionary of the descriptions of used measurements.  
    '''  
    self.measurements = measurements
    self.instanceMeasurements = instanceMeasurements
    self.svWeights = dict()
    self.name = name
    self.workflowFile = workflowFile
    self.artefactFile = artefactFile
    self.workflowModifier = workflowModifier
    self.svWeights = svWeights
    self.valueNames = valueNames
    self.valueDescriptions = valueDescriptions
    
  @property
  def svMeasure(self):
    '''Convinience property that computes the single value measure usgin the
       measurements and the svWeights. If svWeights is None a weight of 1 for
       all measurements is assumed. If svWeights is defined, all measurements
       not explicitly weighted will have the weight 0.'''
    
    result = 0.0
    
    for valueName in self.measurements:
      weight = 0.0
      if self.svWeights is None:
        weight = 1.0
      else:
        try:
          weight = self.svWeights[valueName]
        except:
          pass
        
      try:
        result = result + weight * self.measurements[valueName]
      except TypeError:
        pass #if we cannot weight and add an measurment (because it is None), we just ignore it.

      
    return result
  

XML_NAMESPACE = "http://www.dkfz.de/en/sidt/avid"
XML_NAMESPACE_DICT = {"avid":XML_NAMESPACE}
CURRENT_XML_VERSION = "1.0"

XML_ATTR_VERSION = "version"
XML_ATTR_KEY = "key"
XML_EVALUATION_RESULT = "avid:evaluation_result"
XML_NAME = "avid:name"
XML_WORKFLOWFILE = "avid:workflow_file"
XML_ARTEFACTFILE = "avid:artefact_file"
XML_SV_MEASUREMENT = "avid:sv_measurement"
XML_SV_WEIGHTS = "avid:sv_weights"
XML_SV_WEIGHT = "avid:sv_weight"
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

def loadEvaluationResult(filePath):
  '''Loads a evaluation result from an xml file.
  @param filePath Path where the evaluation result file is located.
  '''
  result = EvaluationResult({}, {})
 
  if not os.path.isfile(filePath):
    raise ValueError("Cannot load evaluation result from file. File does not exist. File path: "+str(filePath))
  
  tree = ElementTree.parse(filePath)
  root = tree.getroot()
  
  if root.tag != "{"+XML_NAMESPACE+"}evaluation_result":
    raise ValueError("XML has not the correct root element. Must be 'evaluation_result', but is: "+root.tag)
  
  node = root.find(XML_EVALUATION_RESULT+'/'+XML_NAME, XML_NAMESPACE_DICT)
  try:
    result.name = node.text
  except:
    raise ValueError('XML has no valid name element')

  node = root.find(XML_EVALUATION_RESULT+'/'+XML_WORKFLOWFILE, XML_NAMESPACE_DICT)
  try:
    result.workflowFile = node.text
  except:
    raise ValueError('XML has no valid workflow file element')
  
  result.workflowModifier = {}
  for modNode in root.findall(XML_EVALUATION_RESULT+'/'+XML_WORKFLOW_MODS+'/'+XML_WORKFLOW_MOD, XML_NAMESPACE_DICT):
    try:
      result.workflowModifier[modNode.attrib[XML_ATTR_KEY]] = modNode.text
    except:
      raise ValueError('XML has an invalid workflow modifier.')
    
  node = root.find(XML_EVALUATION_RESULT+'/'+XML_ARTEFACTFILE, XML_NAMESPACE_DICT)
  try:
    result.artefactFile = node.text
  except:
    raise ValueError('XML has no valid artefact file element')
 
  for mNode in root.findall(XML_EVALUATION_RESULT+'/'+XML_MEASUREMENTS+'/'+XML_MEASUREMENT, XML_NAMESPACE_DICT):
    try:
      result.measurements[mNode.attrib[XML_ATTR_KEY]] = float(mNode.text)
    except:
      raise ValueError('XML has an invalid measurement.')

  for iNode in root.findall(XML_EVALUATION_RESULT+'/'+XML_INSTANCES+'/'+XML_INSTANCE, XML_NAMESPACE_DICT):
    defValues = dict()
    for dNode in iNode.findall(XML_INSTANCE_DESCRIPTOR+'/'+XML_DEF_VALUE, XML_NAMESPACE_DICT):
      try:
        defValues[dNode.attrib[XML_ATTR_KEY]] = dNode.text
      except:
        raise ValueError('XML has an invalid instance descriptor element')
    desc = EvalInstanceDescriptor(defValues)
    
    measures = dict()
    for mNode in iNode.findall(XML_MEASUREMENTS+'/'+XML_MEASUREMENT, XML_NAMESPACE_DICT):
      try:
        measures[mNode.attrib[XML_ATTR_KEY]] = float(mNode.text)
      except:
        raise ValueError('XML has an invalid instance measurement.')
    
    result.instanceMeasurements[desc] = measures

  for iNode in root.findall(XML_EVALUATION_RESULT+'/'+XML_MEASUREMENTS_INFO+'/'+XML_INFO, XML_NAMESPACE_DICT):  
    node = iNode.find(XML_VALUE_NAME, XML_NAMESPACE_DICT)
    try:
      result.valueNames[node.attrib[XML_ATTR_KEY]] = node.text
    except:
      pass
    node = iNode.find(XML_VALUE_DESC, XML_NAMESPACE_DICT)
    try:
      result.valueDescriptions[node.attrib[XML_ATTR_KEY]] = node.text
    except:
      pass

  return result


def xml_indent(elem, level=0):
  '''
  copy and paste from http://effbot.org/zone/element-lib.htm#prettyprint
  it basically walks your tree and adds spaces and newlines so the tree is
  printed in a nice way
  '''
  i = "\n" + level*"  "
  if len(elem):
    if not elem.text or not elem.text.strip():
      elem.text = i + "  "
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
    for elem in elem:
      xml_indent(elem, level+1)
    if not elem.tail or not elem.tail.strip():
      elem.tail = i
  else:
    if level and (not elem.tail or not elem.tail.strip()):
      elem.tail = i

def saveEvaluationResult(filePath, evalResult):
  builder = ElementTree.TreeBuilder()
 
  builder.start(XML_EVALUATION_RESULT, {XML_ATTR_VERSION : CURRENT_XML_VERSION, "xmlns:avid":XML_NAMESPACE})
  
  builder.start(XML_NAME, {})
  builder.data(str(evalResult.name))
  builder.end(XML_NAME)
  
  builder.start(XML_WORKFLOWFILE, {})
  builder.data(str(evalResult.workflowFile))
  builder.end(XML_WORKFLOWFILE)

  builder.start(XML_WORKFLOW_MODS, {})
  for mID in evalResult.workflowModifier:
    builder.start(XML_WORKFLOW_MOD, {XML_ATTR_KEY : mID})
    builder.data(str(evalResult.workflowModifier[mID]))
    builder.end(XML_WORKFLOW_MOD)
  builder.end(XML_WORKFLOW_MODS)

  builder.start(XML_ARTEFACTFILE, {})
  builder.data(str(evalResult.artefactFile))
  builder.end(XML_ARTEFACTFILE)

  builder.start(XML_SV_MEASUREMENT, {})
  builder.data(str(evalResult.svMeasure))
  builder.end(XML_SV_MEASUREMENT)

  builder.start(XML_SV_WEIGHTS, {})
  try:
    for mID in evalResult.svWeights:
      builder.start(XML_SV_WEIGHT, {XML_ATTR_KEY : mID})
      builder.data(str(evalResult.svWeights[mID]))
      builder.end(XML_SV_WEIGHT)
  except:
    pass
  builder.end(XML_SV_WEIGHTS)

  builder.start(XML_MEASUREMENTS, {})
  for mID in evalResult.measurements:
    builder.start(XML_MEASUREMENT, {XML_ATTR_KEY : mID})
    builder.data(str(evalResult.measurements[mID]))
    builder.end(XML_MEASUREMENT)
  builder.end(XML_MEASUREMENTS)

  builder.start(XML_INSTANCES, {})
  for desc in evalResult.instanceMeasurements:
    builder.start(XML_INSTANCE, {})

    builder.start(XML_INSTANCE_DESCRIPTOR, {})
    builder.start(XML_INSTANCE_ID, {})
    builder.data(str(desc.ID))
    builder.end(XML_INSTANCE_ID)
    
    for defValue in desc._definingValues:
      builder.start(XML_DEF_VALUE, {XML_ATTR_KEY : defValue})
      builder.data(str(desc._definingValues[defValue]))
      builder.end(XML_DEF_VALUE)
    builder.end(XML_INSTANCE_DESCRIPTOR)
      
    builder.start(XML_MEASUREMENTS, {})
    for mID in evalResult.instanceMeasurements[desc]:
      builder.start(XML_MEASUREMENT, {XML_ATTR_KEY : mID})
      builder.data(str(evalResult.instanceMeasurements[desc][mID]))
      builder.end(XML_MEASUREMENT)
    builder.end(XML_MEASUREMENTS)

    builder.end(XML_INSTANCE)

  builder.end(XML_INSTANCES)

  builder.start(XML_MEASUREMENTS_INFO, {})
  keys = set(evalResult.valueNames.keys()+evalResult.valueDescriptions.keys())
  
  for key in keys:
    builder.start(XML_INFO, {XML_ATTR_KEY : key})

    if key in evalResult.valueNames:
      builder.start(XML_VALUE_NAME, {})
      builder.data(str(evalResult.valueNames[key]))
      builder.end(XML_VALUE_NAME)

    if key in evalResult.valueDescriptions:
      builder.start(XML_VALUE_DESC, {})
      builder.data(str(evalResult.valueDescriptions[key]))
      builder.end(XML_VALUE_DESC)
      
    builder.end(XML_INFO)
      
  builder.end(XML_MEASUREMENTS_INFO)
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
  
  tree.write(filePath, xml_declaration = True)

