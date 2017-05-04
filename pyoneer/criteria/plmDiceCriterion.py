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
import logging

from avid.common import AVIDUrlLocater
from avid.externals.plastimatch import parseDiceResult
from ..criteria import MetricCriterionBase
from avid.common.artefact import getArtefactProperty
from avid.common.artefact import defaultProps as artefactProps
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
  MID_TP = 'pyoneer.criteria.PlmDiceCriterion.TP'
  MID_TN = 'pyoneer.criteria.PlmDiceCriterion.TN'
  MID_FN = 'pyoneer.criteria.PlmDiceCriterion.FN'
  MID_FP = 'pyoneer.criteria.PlmDiceCriterion.FP'
  MID_DICE = 'pyoneer.criteria.PlmDiceCriterion.DICE'
  MID_SE = 'pyoneer.criteria.PlmDiceCriterion.SE'
  MID_SP = 'pyoneer.criteria.PlmDiceCriterion.SP'
  MID_Hausdorff = 'pyoneer.criteria.PlmDiceCriterion.hausdorff'
  MID_HausdorffAvg = 'pyoneer.criteria.PlmDiceCriterion.hausdorff.avg'
  MID_HausdorffMaxAvg = 'pyoneer.criteria.PlmDiceCriterion.hausdorff.maxavg'
  MID_HausdorffP95 = 'pyoneer.criteria.PlmDiceCriterion.hausdorff.p95'
  MID_HausdorffBoundary = 'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary'
  MID_HausdorffBoundaryAvg = 'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.avg'
  MID_HausdorffBoundaryMaxAvg = 'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.maxavg'
  MID_HausdorffBoundaryP95 = 'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.p95'
  
  DICE_KEYS = ['FN', 'FP', 'DICE', 'SE', 'SP',
               'Hausdorff distance', 'Avg average Hausdorff distance',
               'Max average Hausdorff distance', 'Percent (0.95) Hausdorff distance',
               'Hausdorff distance (boundary)', 'Avg average Hausdorff distance (boundary)',
               'Max average Hausdorff distance (boundary)', 'Percent (0.95) Hausdorff distance (boundary)']

  MAPPING_CRITERION_ID_2_PLM_ID = {MID_TP: 'TP',
                                   MID_TN: 'TN',
                                   MID_FN: 'FN',
                                   MID_FP: 'FP',
                                   MID_DICE: 'DICE',
                                   MID_SE: 'SE',
                                   MID_SP: 'SP',
                                   MID_Hausdorff: 'Hausdorff distance',
                                   MID_HausdorffAvg: 'Avg average Hausdorff distance',
                                   MID_HausdorffMaxAvg: 'Max average Hausdorff distance',
                                   MID_HausdorffP95: 'Percent (0.95) Hausdorff distance',
                                   MID_HausdorffBoundary: 'Hausdorff distance (boundary)',
                                   MID_HausdorffBoundaryAvg: 'Avg average Hausdorff distance (boundary)',
                                   MID_HausdorffBoundaryMaxAvg: 'Max average Hausdorff distance (boundary)',
                                   MID_HausdorffBoundaryP95: 'Percent (0.95) Hausdorff distance (boundary)'}

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
    
    if len(relevantArtefacts['referenceSelector']) == 1 and len(relevantArtefacts['testSelector']) == 1:
      
      plmResult = self._callPlastimatchDice(relevantArtefacts['referenceSelector'][0], relevantArtefacts['testSelector'][0])

      result = dict()
      for key in self.MAPPING_CRITERION_ID_2_PLM_ID:
          try:
              result[key] = plmResult[self.MAPPING_CRITERION_ID_2_PLM_ID[key]]
          except:
              result[key] = None
    else:
      global logger
      logger.error("Error in plmDiceCriterion. Invalid number of relevant artifacts: %s", relevantArtefacts)
         
    return result

  def _callPlastimatchDice(self, reference, test):
    refPath = getArtefactProperty(reference,artefactProps.URL)
    testPath = getArtefactProperty(test,artefactProps.URL)
    
    execURL = AVIDUrlLocater.getExecutableURL(None, "plastimatch")
    
    call = [execURL, 'dice', refPath, testPath,'--all']
    
    result = None
    p = subprocess.Popen(call, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate()

    if err == 0:
      global logger
      logger.error("Error in plmDiceCriterion when calling plastimatch. Error information: %s", errors.getvalue())
    else:
        result = parseDiceResult(output)

    return result
