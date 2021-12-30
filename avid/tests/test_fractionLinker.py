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
from avid.linkers import FractionLinker

class TestFractionLinker(unittest.TestCase):
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

    self.selections1 = [[self.a1], [self.a2], [self.a3], [self.a4], [self.a5], [self.a6], [self.a7], [self.a8], [self.a9], [self.a10]]
    self.selections2 = [[self.a1], [self.a2]]
    self.selections3 = [[self.a1, self.a2], [self.a3, self.a1], [self.a2, self.a3]]
    self.selections4 = [[self.a1], [self.a2], [self.a1, self.a2], [self.a3, self.a1, self.a2], [self.a2, self.a3, self.a6]]

  def checkSelections(self, refSelections, testSelections):
    self.assertEqual(len(testSelections), len(refSelections))

    for pos,refSelection in enumerate(refSelections):
      self.assertEqual(len(testSelections[pos]), len(refSelection))
      for posArtefact, artefact in enumerate(refSelection):
        self.assertIn(artefact, testSelections[pos])

  def test_FractionLinker(self):
    linker = FractionLinker()
    selection = linker.getLinkedSelection(2, self.selections1,self.selections1)
    self.checkSelections([[self.a3],[self.a4]], selection)

    linker = FractionLinker()
    selection = linker.getLinkedSelection(2, self.selections1,self.selections2)
    self.checkSelections([], selection)

    linker = FractionLinker(True)
    selection = linker.getLinkedSelection(2, self.selections1,self.selections2)
    self.checkSelections([[self.a2]], selection)

  def test_FractionLinker_options(self):
    linker = FractionLinker(useClosestPast=False, allowOnlyFullLinkage=False, performInternalLinkage=False)
    selection = linker.getLinkedSelection(0, self.selections3,self.selections4)
    self.checkSelections([[self.a1],[self.a1, self.a2]], selection)

    selection = linker.getLinkedSelection(1, self.selections3,self.selections4)
    self.checkSelections([[self.a3, self.a1, self.a2]], selection)

    selection = linker.getLinkedSelection(2, self.selections3,self.selections4)
    self.checkSelections([[self.a2],[self.a2, self.a3, self.a6]], selection)

    linker = FractionLinker(useClosestPast=False, allowOnlyFullLinkage=False, performInternalLinkage=True)
    selection = linker.getLinkedSelection(0, self.selections3,self.selections4)
    self.checkSelections([[self.a1, None],[self.a1, self.a2]], selection)

    selection = linker.getLinkedSelection(1, self.selections3,self.selections4)
    self.checkSelections([[self.a3, self.a1],[self.a3, None]], selection)

    selection = linker.getLinkedSelection(2, self.selections3,self.selections4)
    self.checkSelections([[self.a2, None],[self.a2, self.a3]], selection)

    linker = FractionLinker(useClosestPast=False, allowOnlyFullLinkage=True, performInternalLinkage=False)
    selection = linker.getLinkedSelection(0, self.selections3,self.selections4)
    self.checkSelections([[self.a1, self.a2]], selection)

    selection = linker.getLinkedSelection(1, self.selections3,self.selections4)
    self.checkSelections([], selection)

    selection = linker.getLinkedSelection(2, self.selections3,self.selections4)
    self.checkSelections([], selection)

    linker = FractionLinker(useClosestPast=False, allowOnlyFullLinkage=True, performInternalLinkage=True)
    selection = linker.getLinkedSelection(0, self.selections3,self.selections4)
    self.checkSelections([[self.a1, self.a2]], selection)

    selection = linker.getLinkedSelection(1, self.selections3,self.selections4)
    self.checkSelections([[self.a3, self.a1]], selection)

    selection = linker.getLinkedSelection(2, self.selections3,self.selections4)
    self.checkSelections([[self.a2, self.a3]], selection)

    linker = FractionLinker(useClosestPast=True, allowOnlyFullLinkage=False, performInternalLinkage=False)
    selection = linker.getLinkedSelection(0, self.selections3,self.selections4)
    self.checkSelections([[self.a1],[self.a1, self.a2]], selection)

    selection = linker.getLinkedSelection(1, self.selections3,self.selections4)
    self.checkSelections([[self.a3, self.a1, self.a2]], selection)

    selection = linker.getLinkedSelection(2, self.selections3,self.selections4)
    self.checkSelections([[self.a2],[self.a2, self.a3, self.a6]], selection)

    linker = FractionLinker(useClosestPast=True, allowOnlyFullLinkage=False, performInternalLinkage=True)
    selection = linker.getLinkedSelection(0, self.selections3,self.selections4)
    self.checkSelections([[self.a1, self.a1],[self.a1, self.a2]], selection)

    selection = linker.getLinkedSelection(1, self.selections3,self.selections4)
    self.checkSelections([[self.a3, self.a1],[self.a3, None]], selection)

    selection = linker.getLinkedSelection(2, self.selections3,self.selections4)
    self.checkSelections([[self.a2, self.a2],[self.a2, self.a3]], selection)

    linker = FractionLinker(useClosestPast=True, allowOnlyFullLinkage=True, performInternalLinkage=False)
    selection = linker.getLinkedSelection(0, self.selections3,self.selections4)
    self.checkSelections([[self.a1, self.a2]], selection)

    selection = linker.getLinkedSelection(1, self.selections3,self.selections4)
    self.checkSelections([[self.a1, self.a2]], selection)

    selection = linker.getLinkedSelection(2, self.selections3,self.selections4)
    self.checkSelections([[self.a1, self.a2]], selection)

    linker = FractionLinker(useClosestPast=True, allowOnlyFullLinkage=True, performInternalLinkage=True)
    selection = linker.getLinkedSelection(0, self.selections3,self.selections4)
    self.checkSelections([[self.a1, self.a1],[self.a1, self.a2]], selection)

    selection = linker.getLinkedSelection(1, self.selections3,self.selections4)
    self.checkSelections([[self.a3, self.a1]], selection)

    selection = linker.getLinkedSelection(2, self.selections3,self.selections4)
    self.checkSelections([[self.a2, self.a2],[self.a2, self.a3]], selection)


  def test_FractionLinker_empty_secondary(self):
    linker = FractionLinker()
    selection = linker.getLinkedSelection(2, self.selections1, [])
    self.assertEqual(len(selection), 0)
  
    linker = FractionLinker(True)
    selection = linker.getLinkedSelection(2, self.selections1, [])
    self.assertEqual(len(selection), 0)


if __name__ == '__main__':
    unittest.main()