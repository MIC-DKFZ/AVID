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
from avid.linkers import TimePointProximityLinker

class TestProximityLinker(unittest.TestCase):
  def setUp(self):
    self.a1 = artefactGenerator.generateArtefactEntry("Case1", None, 10, "Action1", "result", "dummy", None)
    self.a2 = artefactGenerator.generateArtefactEntry("Case2", None, 1, "Action1", "result", "dummy", None)

    self.a3 = artefactGenerator.generateArtefactEntry("Case1", None, 1, "Action2", "result", "dummy", None)
    self.a4 = artefactGenerator.generateArtefactEntry("Case1", None, 3, "Action2", "result", "dummy", None)
    self.a5 = artefactGenerator.generateArtefactEntry("Case1", None, 8, "Action2", "result", "dummy", None)
    self.a6 = artefactGenerator.generateArtefactEntry("Case1", None, 8, "Action3", "result", "dummy", None)
    self.a7 = artefactGenerator.generateArtefactEntry("Case1", None, 100, "Action3", "result", "dummy", None)
    self.a8 = artefactGenerator.generateArtefactEntry("Case2", None, 3, "Action1", "result", "dummy", None)
    self.a9 = artefactGenerator.generateArtefactEntry("Case2", None, 7, "Action1", "result", "dummy", None)
    self.a10 = artefactGenerator.generateArtefactEntry("Case2", None, 10, "Action2", "result", "dummy", None)
    self.a11 = artefactGenerator.generateArtefactEntry("Case3", "a", 10, "Action2", "result", "dummy", None)
    self.a12 = artefactGenerator.generateArtefactEntry("Case4", "1", 1, "Action3", "result", "dummy", None)

    self.data = [[self.a1],[self.a2]]
    self.data2 = [[self.a3],[self.a4],[self.a5],[self.a6],[self.a7],[self.a8],[self.a9],[self.a10],[self.a11],[self.a12]]

  def test_TimePointProximityLinker(self):
    linker = TimePointProximityLinker()
    selections = linker.getLinkedSelection(0, self.data, self.data2)
    self.assertEqual(len(selections), 2)
    self.assertEqual(len(selections[0]), 1)
    self.assertEqual(len(selections[1]), 1)
    self.assertIn(self.a5, selections[0])
    self.assertIn(self.a6, selections[1])

    selections = linker.getLinkedSelection(1, self.data, self.data2)
    self.assertEqual(len(selections), 1)
    self.assertEqual(len(selections[0]), 1)
    self.assertIn(self.a8, selections[0])

if __name__ == '__main__':
    unittest.main()