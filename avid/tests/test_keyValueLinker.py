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

    self.data = [[self.a1],[self.a2],[self.a3],[self.a4],[self.a5],[self.a6],[self.a7],[self.a8],[self.a9],[self.a10],
                 [self.a1, self.a2],[self.a1, self.a2, self.a3],[self.a1, self.a5],[self.a5, self.a9]]
    self.data2 = [[self.a1, self.a2],[self.a3 , self.a4],[self.a4, self.a5],[self.a5, self.a6, self.a7],[self.a8, self.a9, self.a10]]


  def checkSelections(self, refSelections, testSelections):
    self.assertEqual(len(testSelections), len(refSelections))

    for pos,refSelection in enumerate(refSelections):
      self.assertEqual(len(testSelections[pos]), len(refSelection))
      for posArtefact, artefact in enumerate(refSelection):
        self.assertIn(artefact, testSelections[pos])

  def test_CaseLinker_default(self):
    #check default settings
    linker = CaseLinker()
    selections = linker.getLinkedSelection(2, self.data,self.data)
    self.checkSelections([[self.a1],[self.a2],[self.a3],[self.a4]], selections)

    selections = linker.getLinkedSelection(4, self.data,self.data)
    self.checkSelections([[self.a5],[self.a6],[self.a7],[self.a8]], selections)

    selections = linker.getLinkedSelection(1, self.data2, self.data2)
    self.checkSelections([[self.a1, self.a2],[self.a3 , self.a4],[self.a4 , self.a5]], selections)

    selections = linker.getLinkedSelection(2, self.data2, self.data2)
    self.checkSelections([[self.a4 , self.a5]], selections)

    selections = linker.getLinkedSelection(3, self.data2, self.data2)
    self.checkSelections([[self.a5, self.a6, self.a7], [self.a8, self.a9, self.a10]], selections)

  def test_CaseLinker_internallinkageOn(self):
    linker = CaseLinker(performInternalLinkage=True, allowOnlyFullLinkage=True)
    selections = linker.getLinkedSelection(2, self.data,self.data)
    self.checkSelections([[self.a1],[self.a2],[self.a3],[self.a4]], selections)

    selections = linker.getLinkedSelection(4, self.data,self.data)
    self.checkSelections([[self.a5],[self.a6],[self.a7],[self.a8]], selections)

    selections = linker.getLinkedSelection(1, self.data2, self.data2)
    self.checkSelections([[self.a1, self.a1],[self.a3 , self.a3],[self.a4 , self.a4]], selections)

    selections = linker.getLinkedSelection(2, self.data2, self.data2)
    self.checkSelections([[self.a4 , self.a5]], selections)

    selections = linker.getLinkedSelection(3, self.data2, self.data2)
    self.checkSelections([[self.a5, self.a5, self.a5], [self.a8, self.a8, self.a8]], selections)

    linker = CaseLinker(performInternalLinkage=True, allowOnlyFullLinkage=False)
    selections = linker.getLinkedSelection(2, self.data,self.data)
    self.checkSelections([[self.a1],[self.a2],[self.a3],[self.a4]], selections)

    selections = linker.getLinkedSelection(4, self.data,self.data)
    self.checkSelections([[self.a5],[self.a6],[self.a7],[self.a8]], selections)

    selections = linker.getLinkedSelection(1, self.data2, self.data2)
    self.checkSelections([[self.a1, self.a1],[self.a3 , self.a3],[self.a4 , self.a4]], selections)

    selections = linker.getLinkedSelection(2, self.data2, self.data2)
    self.checkSelections([[self.a1 , None],[self.a3 , None],[self.a4 , self.a5],[None , self.a5],[None , self.a8]], selections)

    selections = linker.getLinkedSelection(3, self.data2, self.data2)
    self.checkSelections([[self.a5, self.a5, self.a5], [self.a8, self.a8, self.a8]], selections)

  def test_CaseLinker_internallinkageOff(self):
    linker = CaseLinker(performInternalLinkage=False, allowOnlyFullLinkage=True)
    selections = linker.getLinkedSelection(2, self.data,self.data)
    self.checkSelections([[self.a1],[self.a2],[self.a3],[self.a4]], selections)

    selections = linker.getLinkedSelection(4, self.data,self.data)
    self.checkSelections([[self.a5],[self.a6],[self.a7],[self.a8]], selections)

    selections = linker.getLinkedSelection(1, self.data2, self.data2)
    self.checkSelections([[self.a1, self.a2],[self.a3 , self.a4],[self.a4 , self.a5]], selections)

    selections = linker.getLinkedSelection(2, self.data2, self.data2)
    self.checkSelections([[self.a4 , self.a5]], selections)

    selections = linker.getLinkedSelection(3, self.data2, self.data2)
    self.checkSelections([[self.a5, self.a5, self.a5], [self.a8, self.a8, self.a8]], selections)

    linker = CaseLinker(performInternalLinkage=False, allowOnlyFullLinkage=False)
    selections = linker.getLinkedSelection(2, self.data,self.data)
    self.checkSelections([[self.a1],[self.a2],[self.a3],[self.a4],[self.a1, self.a2],[self.a1, self.a2, self.a3],[self.a1, self.a5]], selections)

    selections = linker.getLinkedSelection(4, self.data,self.data)
    self.checkSelections([[self.a5],[self.a6],[self.a7],[self.a8],[self.a1, self.a5],[self.a5, self.a9]], selections)

    selections = linker.getLinkedSelection(1, self.data2, self.data2)
    self.checkSelections([[self.a1, self.a2],[self.a3 , self.a4],[self.a4 , self.a5]], selections)

    selections = linker.getLinkedSelection(2, self.data2, self.data2)
    self.checkSelections(self.data2, selections)

    selections = linker.getLinkedSelection(3, self.data2, self.data2)
    self.checkSelections([[self.a4, self.a5],[self.a5, self.a6, self.a7],[self.a8, self.a9, self.a10]], selections)


  def test_TimePointLinker_default(self):
    linker = TimePointLinker()
    selections = linker.getLinkedSelection(7, self.data,self.data)
    self.checkSelections([[self.a3],[self.a4],[self.a8]], selections)

    selections = linker.getLinkedSelection(1, self.data2, self.data2)
    self.checkSelections([[self.a3 , self.a4],[self.a4, self.a5]], selections)


  def test_TimePointLinker_internalLinkageOn(self):
    linker = TimePointLinker(performInternalLinkage=True, allowOnlyFullLinkage=True)
    selections = linker.getLinkedSelection(7, self.data,self.data)
    self.checkSelections([[self.a3],[self.a4],[self.a8]], selections)

    selections = linker.getLinkedSelection(1, self.data2, self.data2)
    self.checkSelections([[self.a3 , self.a3],[self.a4, self.a4],[self.a8, self.a8]], selections)

    linker = TimePointLinker(performInternalLinkage=True, allowOnlyFullLinkage=False)
    selections = linker.getLinkedSelection(7, self.data,self.data)
    self.checkSelections([[self.a3],[self.a4],[self.a8]], selections)

    selections = linker.getLinkedSelection(1, self.data2, self.data2)
    self.checkSelections([[self.a3 , self.a3],[self.a4, self.a4],[self.a8, self.a8]], selections)


  def test_KeyValueLinker(self):
    linker = KeyValueLinker(artefactProps.ACTIONTAG)
    selections = linker.getLinkedSelection(0, self.data,self.data)
    self.checkSelections([[self.a1],[self.a2],[self.a5],[self.a6]], selections)

    selections = linker.getLinkedSelection(1, self.data2, self.data2)
    self.checkSelections([[self.a3 , self.a4]], selections)

    weakLinker = KeyValueLinker(artefactProps.ACTIONTAG, allowOnlyFullLinkage=False)
    selections = weakLinker.getLinkedSelection(1, self.data2, self.data2)
    self.checkSelections([[self.a3 , self.a4],[self.a4, self.a5],[self.a5, self.a6, self.a7],[self.a8, self.a9, self.a10]], selections)

    linker = KeyValueLinker(artefactProps.ACTIONTAG)
    selections = linker.getLinkedSelection(0, self.data,[])
    self.assertEqual(len(selections), 0)


if __name__ == '__main__':
    unittest.main()