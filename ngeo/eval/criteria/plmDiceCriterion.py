

from ..criteria import MetricCriterionBase
from avid.common.artefact import getArtefactProperty, defaultProps
from avid.selectors.keyValueSelector import ActionTagSelector
import subprocess
from StringIO import StringIO


logger = logging.getLogger(__name__)

class PlmDiceCriterion(MetricCriterionBase):
  '''Criterion that evaluates the difference between to masks using the
     plastimatch dice..
     The criterion assumes as default that the reference is selected be the tag
     "Reference" and is an itk image. The test image is by default selected by
     the tag "Test". 
  '''

  #Measurement value IDs.
  MID_TP = 'ngeo.eval.criteria.PlmDiceCriterion.TP'
  MID_TN = 'ngeo.eval.criteria.PlmDiceCriterion.TN'
  MID_FN = 'ngeo.eval.criteria.PlmDiceCriterion.FN'
  MID_FP = 'ngeo.eval.criteria.PlmDiceCriterion.FP'
  MID_DICE = 'ngeo.eval.criteria.PlmDiceCriterion.DICE'
  MID_SE = 'ngeo.eval.criteria.PlmDiceCriterion.SE'
  MID_SP = 'ngeo.eval.criteria.PlmDiceCriterion.SP'
  MID_Hausdorff = 'ngeo.eval.criteria.PlmDiceCriterion.hausdorff'
  MID_HausdorffAvg = 'ngeo.eval.criteria.PlmDiceCriterion.hausdorff.avg'
  MID_HausdorffMaxAvg = 'ngeo.eval.criteria.PlmDiceCriterion.hausdorff.maxavg'
  MID_HausdorffP95 = 'ngeo.eval.criteria.PlmDiceCriterion.hausdorff.p95'
  MID_HausdorffBoundary = 'ngeo.eval.criteria.PlmDiceCriterion.hausdorff.boundary'
  MID_HausdorffBoundaryAvg = 'ngeo.eval.criteria.PlmDiceCriterion.hausdorff.boundary.avg'
  MID_HausdorffBoundaryMaxAvg = 'ngeo.eval.criteria.PlmDiceCriterion.hausdorff.boundary.maxavg'
  MID_HausdorffBoundaryP95 = 'ngeo.eval.criteria.PlmDiceCriterion.hausdorff.boundary.p95'
  
  MAPPING_PLM_ID_2_CRITERION_ID = {PlmDiceCriterion.MID_TP: 'TP',
                                   PlmDiceCriterion.MID_TN: 'TN'}
  
  def __init__(self, referenceSelector = ActionTagSelector('Reference'), testSelector = ActionTagSelector('Test')):
    valuesInfo = { self.MID_TP: ['True Positives','Number of true positive voxels.'],
                   self.MID_TN: ['True Negatives','Number of true negative voxels.'],
                   self.MID_FN: ['False Negatives','Number of false negative voxels.'],
                   self.MID_FP: ['False Positives','Number of false positive voxels.'],
                   self.MID_DICE: ['Dice Coefficient','Dice Coefficient'],
                   self.MID_SE: ['Sensitivity','Sensitivity of the test covering the reference.'],
                   self.MID_SP: ['Specificity','Specificity of the test covering the reference.'],
                   self.MID_Hausdorff: ['Hausdorff distance','Hausdorff distance between the masks.'],
                   self.MID_HausdorffAvg: ['Average Hausdorff distance','Average Hausdorff distance between the masks.'],
                   self.MID_HausdorffMaxAvg: ['Average Hausdorff distance','Average Hausdorff distance between the masks.'],
                   self.MID_HausdorffP95: ['P95 Hausdorff distance','95-Percentile of Hausdorff distance between the masks.'],
                   self.MID_HausdorffBoundary: ['Hausdorff distance boundary','Hausdorff distance between the boundaries of the the masks.'],
                   self.MID_HausdorffBoundaryAvg: ['Average Hausdorff distance boundary','Average Hausdorff distance between the boundaries of the masks.'],
                   self.MID_HausdorffBoundaryMaxAvg: ['Average Hausdorff distance boundary','Average Hausdorff distance between the boundaries of the the masks.'],
                   self.MID_HausdorffBoundaryP95: ['P95 Hausdorff distance boundary','95-Percentile of Hausdorff distance between the boundaries of the the masks.']}

    MetricCriterionBase.__init__(self, valuesInfo = valuesInfo)
    self.setSelectors(referenceSelector = referenceSelector, testSelector = testSelector)  

  def _evaluateInstance(self, relevantArtefacts):
    '''Internal method that really does the evaluation regaring the passed list
    of relevant artefacts. It will be called by evaluateInstance(), which generates
    the passed dictionary.
    @param relevantArtefacts: dictionary of relevant artefacts (may be lists).
    The used keys are defined by the derived classes and are the variable names
    used in the setSelectors call.
    @return: Returns a dictionary with the criterion measurements. Key is the
    value ID. The dict value is the measurement value(s). 
     '''
    result = None
    
    if len(relevantArtefacts['referenceSelector']) == 1 and len(relevantArtefacts['referenceSelector']) == 1:
      
      plmResult = self._callPlastimatchDice(relevantArtefacts['referenceSelector'][0], relevantArtefacts['referenceSelector'][0])
      
      result = {valueID: plmResult[self.MAPPING_PLM_ID_2_CRITERION_ID[valueID]] for valueID in self._valueNames}
      
    else:
      global logger
      logger.error("Error in plmDiceCriterion. Invalid number of relevant artifacts: %s", relevantArtefacts)
         
    return result

  def _callPlastimatchDice(self, reference, test):
    refPath = getArtefactProperty(reference,artefactProps.URL)
    testPath = getArtefactProperty(test,artefactProps.URL)
    
    execURL = AVIDUrlLocater.getExecutableURL(self._session, "plastimatch", self._actionConfig)
    
    callStr = '"' + execURL + '" dice ' + ' "' + refPath + '"' + ' "' + testPath +'" --all'
    
    output = StringIO
    errors = StringIO
    result = None
    if not subprocess.call(callStr,stdout = output, stderr = errors) == 0:
      global logger
      logger.error("Error in plmDiceCriterion when calling plastimatch. Error information: %s", errors.getvalue())
    else:
      result = parseDiceResult(output.getvalue())
    
    return result
