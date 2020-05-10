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

from avid.linkers import KeyValueLinker
from avid.linkers import CaseLinker
from avid.linkers import TimePointLinker

class TestKeyValueLinker(unittest.TestCase):
  def setUp(self):
    self.a1 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action1", "result", "dummy", None)
    self.a2 = artefactGenerator.generateArtefactEntry("Case1", None, 1, "Action1", "result", "dummy", None)
    self.a3 = artefactGenerator.generateArtefactEntry("Case1", None, 2, "Action2", "result", "dummy", None)
    self.a4 = artefactGenerator.generateArtefactEntry("Case1", None, 2, "Action3", "result", "dummy", None)
    self.a5 = artefactGenerator.generateArtefactEntry("Case2", None, 0, "Action1", "result", "dummy", None)
    self.a6 = artefactGenerator.generateArtefactEntry("Case2", None, 1, "Action1", "result", "dummy", None)
    self.a7 = artefactGenerator.generateArtefactEntry("Case2", None, 1, "Action2", "result", "dummy", None)
    self.a8 = artefactGenerator.generateArtefactEntry("Case2", None, 2, "Action2", "result", "dummy", None)
    self.a9 = artefactGenerator.generateArtefactEntry("Case3", "a", 0, "Action2", "result", "dummy", None)
    self.a10 = artefactGenerator.generateArtefactEntry("Case4", "1", 0, "Action3", "result", "dummy", None)

    self.data = [[self.a1],[self.a2],[self.a3],[self.a4],[self.a5],[self.a6],[self.a7],[self.a8],[self.a9],[self.a10]]
    self.data2 = [[self.a1, self.a2],[self.a3 , self.a4],[self.a5, self.a6, self.a7],[self.a8, self.a9, self.a10]]



  def test_CaseLinker(self):
    linker = CaseLinker()
    selections = linker.getLinkedSelection(2, self.data,self.data)
    self.assertEqual(len(selections), 4)
    self.assertEqual(len(selections[0]), 1)
    self.assertEqual(len(selections[1]), 1)
    self.assertEqual(len(selections[2]), 1)
    self.assertEqual(len(selections[3]), 1)
    self.assertIn(self.a1, selections[0])
    self.assertIn(self.a2, selections[1])
    self.assertIn(self.a3, selections[2])
    self.assertIn(self.a4, selections[3])

    selections = linker.getLinkedSelection(1, self.data2, self.data2)
    self.assertEqual(len(selections), 2)
    self.assertEqual(len(selections[0]), 2)
    self.assertIn(self.a1, selections[0])
    self.assertIn(self.a2, selections[0])
    self.assertEqual(len(selections[1]), 2)
    self.assertIn(self.a3, selections[1])
    self.assertIn(self.a4, selections[1])

  def test_TimePointLinker(self):
    linker = TimePointLinker()
    selections = linker.getLinkedSelection(7, self.data,self.data)
    self.assertEqual(len(selections), 3)
    self.assertEqual(len(selections[0]), 1)
    self.assertEqual(len(selections[1]), 1)
    self.assertEqual(len(selections[2]), 1)
    self.assertIn(self.a3, selections[0])
    self.assertIn(self.a4, selections[1])
    self.assertIn(self.a8, selections[2])

    selections = linker.getLinkedSelection(1, self.data2, self.data2)
    self.assertEqual(len(selections), 2)
    self.assertEqual(len(selections[0]), 2)
    self.assertIn(self.a3, selections[0])
    self.assertIn(self.a4, selections[0])
    self.assertEqual(len(selections[1]), 3)
    self.assertIn(self.a8, selections[1])
    self.assertIn(self.a9, selections[1])
    self.assertIn(self.a10, selections[1])

  def test_KeyValueLinker(self):
    linker = KeyValueLinker(artefactProps.ACTIONTAG)
    selections = linker.getLinkedSelection(0, self.data,self.data)
    self.assertEqual(len(selections), 4)
    self.assertEqual(len(selections[0]), 1)
    self.assertEqual(len(selections[1]), 1)
    self.assertEqual(len(selections[2]), 1)
    self.assertEqual(len(selections[3]), 1)
    self.assertIn(self.a1, selections[0])
    self.assertIn(self.a2, selections[1])
    self.assertIn(self.a5, selections[2])
    self.assertIn(self.a6, selections[3])

    selections = linker.getLinkedSelection(1, self.data2, self.data2)
    self.assertEqual(len(selections), 2)
    self.assertEqual(len(selections[0]), 2)
    self.assertIn(self.a3, selections[0])
    self.assertIn(self.a4, selections[0])
    self.assertEqual(len(selections[1]), 3)
    self.assertIn(self.a8, selections[1])
    self.assertIn(self.a9, selections[1])
    self.assertIn(self.a10, selections[1])

    weakLinker = KeyValueLinker(artefactProps.ACTIONTAG, checkAllPrimaryArtefacts=False)
    selections = weakLinker.getLinkedSelection(1, self.data2, self.data2)
    self.assertEqual(len(selections), 3)
    self.assertEqual(len(selections[0]), 2)
    self.assertIn(self.a3, selections[0])
    self.assertIn(self.a4, selections[0])
    self.assertEqual(len(selections[1]), 3)
    self.assertIn(self.a5, selections[1])
    self.assertIn(self.a6, selections[1])
    self.assertIn(self.a7, selections[1])
    self.assertEqual(len(selections[2]), 3)
    self.assertIn(self.a8, selections[2])
    self.assertIn(self.a9, selections[2])
    self.assertIn(self.a10, selections[2])

    linker = KeyValueLinker(artefactProps.ACTIONTAG)
    selections = linker.getLinkedSelection(0, self.data,[])
    self.assertEqual(len(selections), 0)


if __name__ == '__main__':
    unittest.main()