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

import unittest
import avid.common.artefact.generator as artefactGenerator
import avid.common.artefact as artefact
import avid.common.artefact.defaultProps as artefactProps
from avid.common import workflow


class TestArtefact(unittest.TestCase):
  def setUp(self):
    self.a1 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action1", "result", "dummy", "myCoolFile.any")
    self.a2 = artefactGenerator.generateArtefactEntry("Case1", 1, 0, "Action2", "result", "dummy", "myCoolFile.any", "target")
    self.a3 = artefactGenerator.generateArtefactEntry("Case1", 1, 0, "IllegalChars*?", "result", "dummy", "myCoolFile.any")

    self.session = workflow.Session('TestSession', 'test_session_dir')


  def test_getArtefactShortName(self):
    name = artefact.getArtefactShortName(self.a1)
    self.assertEqual(name, 'Action1#0')
    name = artefact.getArtefactShortName(self.a2)
    self.assertEqual(name, 'Action2-target#0')
    name = artefact.getArtefactShortName(self.a3)
    self.assertEqual(name, 'IllegalChars#0')

  def test_generateArtefactPath(self):
    path = artefact.generateArtefactPath(self.session, self.a1)
    self.assertEqual(path, 'test_session_dir\\TestSession\\Action1\\result\\Case1')
    path = artefact.generateArtefactPath(self.session, self.a2)
    self.assertEqual(path, 'test_session_dir\\TestSession\\Action2\\result\\Case1\\1')
    path = artefact.generateArtefactPath(self.session, self.a3)
    self.assertEqual(path, 'test_session_dir\\TestSession\\IllegalChars\\result\\Case1\\1')

  def test_ensureSimilarityRelevantProperty(self):
    self.assertNotIn("ensuredTestProp", artefact.similarityRelevantProperties)
    artefact.ensureSimilarityRelevantProperty("ensuredTestProp")
    self.assertIn("ensuredTestProp", artefact.similarityRelevantProperties)

    propCount = len(artefact.similarityRelevantProperties)
    artefact.ensureSimilarityRelevantProperty("ensuredTestProp")
    self.assertEqual(propCount, len(artefact.similarityRelevantProperties))
    self.assertIn("ensuredTestProp", artefact.similarityRelevantProperties)


if __name__ == '__main__':
    unittest.main()