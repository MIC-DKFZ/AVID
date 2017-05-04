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
import os
import unittest


import avid.common.artefact as artefact
import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact.generator as artefactGenerator
from pyoneer.criteria.plmDiceCriterion import PlmDiceCriterion as DiceCriterion


class TestSelectors(unittest.TestCase):
  def setUp(self):
    self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "metricsTest")
    self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_metrics")

    self.a1 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Reference", artefactProps.TYPE_VALUE_RESULT, artefactProps.FORMAT_VALUE_ITK, os.path.join(self.testDataDir, "MatchPointLogo.mhd"))
    self.a2 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Test", artefactProps.TYPE_VALUE_RESULT, artefactProps.FORMAT_VALUE_ITK, os.path.join(self.testDataDir, "MatchPointLogoShifted10x-16y-5z.mhd"))

    self.data = list()
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a1)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a2)

    self.a3 = artefactGenerator.generateArtefactEntry("Case2", None, 0, "Reference", artefactProps.TYPE_VALUE_RESULT, artefactProps.FORMAT_VALUE_ITK, os.path.join(self.testDataDir, "MatchPointLogo.mhd"))
    self.a4 = artefactGenerator.generateArtefactEntry("Case2", None, 0, "Test", artefactProps.TYPE_VALUE_RESULT, artefactProps.FORMAT_VALUE_ITK, os.path.join(self.testDataDir, "MatchPointLogo.mhd"))

    self.data2 = list()
    self.data2 = artefact.addArtefactToWorkflowData(self.data2, self.a3)
    self.data2 = artefact.addArtefactToWorkflowData(self.data2, self.a4)

    refCriterion = DiceCriterion()
    self.instanceResultRef = {'pyoneer.criteria.PlmDiceCriterion.TN': 548180.0, 'pyoneer.criteria.PlmDiceCriterion.hausdorff.p95': 15.967952,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.p95': 17.578028,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff': 19.51922, 'pyoneer.criteria.PlmDiceCriterion.SP': 0.962462,
     'pyoneer.criteria.PlmDiceCriterion.FP': 21380.0,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.maxavg': 6.967815,
     'pyoneer.criteria.PlmDiceCriterion.DICE': 0.297635, 'pyoneer.criteria.PlmDiceCriterion.FN': 21380.0,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.avg': 5.234368,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary': 19.51922, 'pyoneer.criteria.PlmDiceCriterion.TP': 9060.0,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.maxavg': 5.312498, 'pyoneer.criteria.PlmDiceCriterion.SE': 0.297635,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.avg': 6.711402}

    self.setResultRef = {'pyoneer.criteria.PlmDiceCriterion.TN.min': 548180.0, 'pyoneer.criteria.PlmDiceCriterion.hausdorff.mean': 9.75961,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.p95.min': 0.0,
     'pyoneer.criteria.PlmDiceCriterion.SE.max': 1.0,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.maxavg.mean': 3.4839075,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.p95.max': 17.578028,
     'pyoneer.criteria.PlmDiceCriterion.FN.min': 0.0, 'pyoneer.criteria.PlmDiceCriterion.TN.max': 569560.0,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.p95.sd': 7.983976,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.maxavg.min': 0.0, 'pyoneer.criteria.PlmDiceCriterion.FN.sd': 10690.0,
     'pyoneer.criteria.PlmDiceCriterion.TP.max': 30440.0,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.avg.max': 6.711402,
     'pyoneer.criteria.PlmDiceCriterion.SP.sd': 0.01876899999999998, 'pyoneer.criteria.PlmDiceCriterion.FP.sd': 10690.0,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.max': 19.51922, 'pyoneer.criteria.PlmDiceCriterion.TP.sd': 10690.0,
     'pyoneer.criteria.PlmDiceCriterion.TN.mean': 558870.0,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.maxavg.sd': 3.4839075,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.maxavg.max': 5.312498,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.p95.mean': 8.789014,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.sd': 9.75961,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.min': 0.0,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.max': 19.51922,
     'pyoneer.criteria.PlmDiceCriterion.DICE.mean': 0.6488175,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.maxavg.mean': 2.656249,
     'pyoneer.criteria.PlmDiceCriterion.TN.sd': 10690.0, 'pyoneer.criteria.PlmDiceCriterion.SP.max': 1.0,
     'pyoneer.criteria.PlmDiceCriterion.TP.min': 9060.0,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.avg.mean': 2.617184,
     'pyoneer.criteria.PlmDiceCriterion.TP.mean': 19750.0, 'pyoneer.criteria.PlmDiceCriterion.DICE.min': 0.297635,
     'pyoneer.criteria.PlmDiceCriterion.DICE.max': 1.0, 'pyoneer.criteria.PlmDiceCriterion.FN.mean': 10690.0,
     'pyoneer.criteria.PlmDiceCriterion.SP.min': 0.962462,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.mean': 9.75961,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.p95.min': 0.0,
     'pyoneer.criteria.MetricCriterionBase.FailedInstances': 0,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.maxavg.max': 6.967815,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.avg.max': 5.234368,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.p95.sd': 8.789014,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.avg.min': 0.0,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.maxavg.min': 0.0,
     'pyoneer.criteria.PlmDiceCriterion.SE.sd': 0.3511825,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.maxavg.sd': 2.656249,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.p95.max': 15.967952,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.p95.mean': 7.983976,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.avg.mean': 3.355701,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.avg.sd': 2.617184,
     'pyoneer.criteria.PlmDiceCriterion.FN.max': 21380.0, 'pyoneer.criteria.PlmDiceCriterion.DICE.sd': 0.3511825,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.min': 0.0,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.sd': 9.75961,
     'pyoneer.criteria.PlmDiceCriterion.FP.max': 21380.0, 'pyoneer.criteria.PlmDiceCriterion.FP.min': 0.0,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.avg.min': 0.0,
     'pyoneer.criteria.PlmDiceCriterion.SE.min': 0.297635, 'pyoneer.criteria.PlmDiceCriterion.SP.mean': 0.981231,
     'pyoneer.criteria.PlmDiceCriterion.SE.mean': 0.6488175,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.avg.sd': 3.355701,
     'pyoneer.criteria.PlmDiceCriterion.FP.mean': 10690.0}

    setResultWithFailRef = {'pyoneer.criteria.PlmDiceCriterion.TN.min': 548180.0, 'pyoneer.criteria.PlmDiceCriterion.hausdorff.mean': 19.51922,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.p95.min': 17.578028,
     'pyoneer.criteria.PlmDiceCriterion.SE.max': 0.297635,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.maxavg.mean': 6.967815,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.p95.max': 17.578028,
     'pyoneer.criteria.PlmDiceCriterion.FN.min': 21380.0, 'pyoneer.criteria.PlmDiceCriterion.TN.max': 548180.0,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.p95.sd': 0.0,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.maxavg.min': 5.312498, 'pyoneer.criteria.PlmDiceCriterion.FN.sd': 0.0,
     'pyoneer.criteria.PlmDiceCriterion.TP.max': 9060.0,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.avg.max': 6.711402,
     'pyoneer.criteria.PlmDiceCriterion.SP.sd': 0.0, 'pyoneer.criteria.PlmDiceCriterion.FP.sd': 0.0,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.max': 19.51922, 'pyoneer.criteria.PlmDiceCriterion.TP.sd': 0.0,
     'pyoneer.criteria.PlmDiceCriterion.TN.mean': 548180.0,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.maxavg.sd': 0.0,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.maxavg.max': 5.312498,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.p95.mean': 17.578028,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.sd': 0.0,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.min': 19.51922,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.max': 19.51922,
     'pyoneer.criteria.PlmDiceCriterion.DICE.mean': 0.297635,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.maxavg.mean': 5.312498,
     'pyoneer.criteria.PlmDiceCriterion.TN.sd': 0.0, 'pyoneer.criteria.PlmDiceCriterion.SP.max': 0.962462,
     'pyoneer.criteria.PlmDiceCriterion.TP.min': 9060.0,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.avg.mean': 5.234368,
     'pyoneer.criteria.PlmDiceCriterion.TP.mean': 9060.0, 'pyoneer.criteria.PlmDiceCriterion.DICE.min': 0.297635,
     'pyoneer.criteria.PlmDiceCriterion.DICE.max': 0.297635, 'pyoneer.criteria.PlmDiceCriterion.FN.mean': 21380.0,
     'pyoneer.criteria.PlmDiceCriterion.SP.min': 0.962462,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.mean': 19.51922,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.p95.min': 15.967952,
     'pyoneer.criteria.MetricCriterionBase.FailedInstances': 1,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.maxavg.max': 6.967815,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.avg.max': 5.234368,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.p95.sd': 0.0,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.avg.min': 5.234368,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.maxavg.min': 6.967815,
     'pyoneer.criteria.PlmDiceCriterion.SE.sd': 0.0, 'pyoneer.criteria.PlmDiceCriterion.hausdorff.maxavg.sd': 0.0,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.p95.max': 15.967952,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.p95.mean': 15.967952,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.avg.mean': 6.711402,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.avg.sd': 0.0, 'pyoneer.criteria.PlmDiceCriterion.FN.max': 21380.0,
     'pyoneer.criteria.PlmDiceCriterion.DICE.sd': 0.0, 'pyoneer.criteria.PlmDiceCriterion.hausdorff.min': 19.51922,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.sd': 0.0,
     'pyoneer.criteria.PlmDiceCriterion.FP.max': 21380.0, 'pyoneer.criteria.PlmDiceCriterion.FP.min': 21380.0,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.avg.min': 6.711402,
     'pyoneer.criteria.PlmDiceCriterion.SE.min': 0.297635, 'pyoneer.criteria.PlmDiceCriterion.SP.mean': 0.962462,
     'pyoneer.criteria.PlmDiceCriterion.SE.mean': 0.297635,
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.avg.sd': 0.0,
     'pyoneer.criteria.PlmDiceCriterion.FP.mean': 21380.0}

    self.namesRef = {'pyoneer.criteria.PlmDiceCriterion.TN.min': 'True Negatives (min)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.mean': 'Hausdorff distance (mean)',
     'pyoneer.criteria.PlmDiceCriterion.TN': 'True Negatives',
     'pyoneer.criteria.PlmDiceCriterion.SE.max': 'Sensitivity (max)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.maxavg.mean': 'Average Hausdorff distance boundary (mean)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff': 'Hausdorff distance',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary': 'Hausdorff distance boundary',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.p95.mean': 'P95 Hausdorff distance boundary (mean)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.p95.min': 'P95 Hausdorff distance boundary (min)',
     'pyoneer.criteria.PlmDiceCriterion.TN.max': 'True Negatives (max)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.p95.sd': 'P95 Hausdorff distance (std dev)',
     'pyoneer.criteria.PlmDiceCriterion.DICE': 'Dice Coefficient',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.maxavg.min': 'Average Hausdorff distance (min)',
     'pyoneer.criteria.PlmDiceCriterion.FN.min': 'False Negatives (min)',
     'pyoneer.criteria.PlmDiceCriterion.FN.sd': 'False Negatives (std dev)',
     'pyoneer.criteria.PlmDiceCriterion.TP.max': 'True Positives (max)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.avg.max': 'Average Hausdorff distance boundary (max)',
     'pyoneer.criteria.PlmDiceCriterion.SP.sd': 'Specificity (std dev)',
     'pyoneer.criteria.PlmDiceCriterion.TP': 'True Positives',
     'pyoneer.criteria.PlmDiceCriterion.FP.sd': 'False Positives (std dev)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.max': 'Hausdorff distance (max)',
     'pyoneer.criteria.PlmDiceCriterion.TP.sd': 'True Positives (std dev)',
     'pyoneer.criteria.PlmDiceCriterion.TN.mean': 'True Negatives (mean)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.maxavg.sd': 'Average Hausdorff distance boundary (std dev)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.maxavg.max': 'Average Hausdorff distance (max)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.p95.max': 'P95 Hausdorff distance boundary (max)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.sd': 'Hausdorff distance (std dev)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.min': 'Hausdorff distance boundary (min)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.max': 'Hausdorff distance boundary (max)',
     'pyoneer.criteria.PlmDiceCriterion.DICE.mean': 'Dice Coefficient (mean)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.maxavg.mean': 'Average Hausdorff distance (mean)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.p95': 'P95 Hausdorff distance boundary',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.avg': 'Average Hausdorff distance boundary',
     'pyoneer.criteria.PlmDiceCriterion.TN.sd': 'True Negatives (std dev)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.maxavg.max': 'Average Hausdorff distance boundary (max)',
     'pyoneer.criteria.PlmDiceCriterion.SP.max': 'Specificity (max)',
     'pyoneer.criteria.PlmDiceCriterion.TP.min': 'True Positives (min)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.avg.mean': 'Average Hausdorff distance (mean)',
     'pyoneer.criteria.PlmDiceCriterion.TP.mean': 'True Positives (mean)',
     'pyoneer.criteria.PlmDiceCriterion.DICE.min': 'Dice Coefficient (min)',
     'pyoneer.criteria.PlmDiceCriterion.DICE.max': 'Dice Coefficient (max)',
     'pyoneer.criteria.PlmDiceCriterion.FN.mean': 'False Negatives (mean)',
     'pyoneer.criteria.PlmDiceCriterion.SP.min': 'Specificity (min)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.mean': 'Hausdorff distance boundary (mean)',
     'pyoneer.criteria.PlmDiceCriterion.SP': 'Specificity', 'pyoneer.criteria.PlmDiceCriterion.FP': 'False Positives',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.p95.min': 'P95 Hausdorff distance (min)',
     'pyoneer.criteria.PlmDiceCriterion.FP.min': 'False Positives (min)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.p95.max': 'P95 Hausdorff distance (max)',
     'pyoneer.criteria.PlmDiceCriterion.FN': 'False Negatives',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.avg.max': 'Average Hausdorff distance (max)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.p95.sd': 'P95 Hausdorff distance boundary (std dev)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.avg.min': 'Average Hausdorff distance (min)',
     'pyoneer.criteria.PlmDiceCriterion.SE': 'Sensitivity',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.maxavg.min': 'Average Hausdorff distance boundary (min)',
     'pyoneer.criteria.PlmDiceCriterion.SE.sd': 'Sensitivity (std dev)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.maxavg.sd': 'Average Hausdorff distance (std dev)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.p95': 'P95 Hausdorff distance',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.p95.mean': 'P95 Hausdorff distance (mean)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.avg.mean': 'Average Hausdorff distance boundary (mean)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.avg.sd': 'Average Hausdorff distance (std dev)',
     'pyoneer.criteria.PlmDiceCriterion.SE.mean': 'Sensitivity (mean)',
     'pyoneer.criteria.PlmDiceCriterion.DICE.sd': 'Dice Coefficient (std dev)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.avg': 'Average Hausdorff distance',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.min': 'Hausdorff distance (min)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.maxavg': 'Average Hausdorff distance boundary',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.sd': 'Hausdorff distance boundary (std dev)',
     'pyoneer.criteria.PlmDiceCriterion.FP.max': 'False Positives (max)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.maxavg': 'Average Hausdorff distance',
     'pyoneer.criteria.MetricCriterionBase.FailedInstances': 'Failures',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.avg.min': 'Average Hausdorff distance boundary (min)',
     'pyoneer.criteria.PlmDiceCriterion.SE.min': 'Sensitivity (min)',
     'pyoneer.criteria.PlmDiceCriterion.SP.mean': 'Specificity (mean)',
     'pyoneer.criteria.PlmDiceCriterion.FN.max': 'False Negatives (max)',
     'pyoneer.criteria.PlmDiceCriterion.hausdorff.boundary.avg.sd': 'Average Hausdorff distance boundary (std dev)',
     'pyoneer.criteria.PlmDiceCriterion.FP.mean': 'False Positives (mean)'}

  def test_PropertyCriterion_instance(self):
    criterion = DiceCriterion()
    
    result = criterion.evaluateInstance(self.data)
    self.assertDictEqual(self.instanceResultRef, result)

    result = criterion.evaluateInstance([])
    self.assertEqual(None, result)
    
    
  def test_PropertyCriterion_set(self):
    criterion = DiceCriterion()
    
    instanceMeasurements = list()
    instanceMeasurements.append(criterion.evaluateInstance(self.data))
    instanceMeasurements.append(criterion.evaluateInstance(self.data2))

    result = criterion.compileSetEvaluation(instanceMeasurements)
    self.assertDictEqual(self.setResultRef, result, 'Check compileSetEvaluation() with normal usage')

  def test_PropertyCriterion_names(self):
    names = DiceCriterion('coolProp').valueNames
    
    self.assertDictEqual(names, self.namesRef)


if __name__ == '__main__':
    unittest.main()