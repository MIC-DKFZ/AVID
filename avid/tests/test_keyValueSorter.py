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
from avid.sorter import KeyValueSorter

class TestKeyValueSorter(unittest.TestCase):
  def setUp(self):
    self.a1 = artefactGenerator.generateArtefactEntry("Case3", "3", 0, "Action1", "result", "dummy", None)
    self.a2 = artefactGenerator.generateArtefactEntry("Case5", "1", 1, "Action1", "result", "dummy", None)
    self.a3 = artefactGenerator.generateArtefactEntry("Case1", "20", 0, "Action2", "result", "dummy", None)
    self.a4 = artefactGenerator.generateArtefactEntry("Case2", "7", 0, "Action1", "result", "dummy", None)
    self.a5 = artefactGenerator.generateArtefactEntry("Case4", "5", 1, "Action1", "result", "dummy", None)

    self.data = list()
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a1)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a2)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a3)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a4)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a5)

  def test_KeyValueSorter(self):
    sorter = KeyValueSorter(key=artefact.defaultProps.CASE)
    selection = sorter.sortSelection(self.data)
    self.assertEqual(len(selection), 5)
    self.assertEqual(self.a3, selection[0])
    self.assertEqual(self.a4, selection[1])
    self.assertEqual(self.a1, selection[2])
    self.assertEqual(self.a5, selection[3])
    self.assertEqual(self.a2, selection[4])

    sorter = KeyValueSorter(key=artefact.defaultProps.CASEINSTANCE)
    selection = sorter.sortSelection(self.data)
    self.assertEqual(len(selection), 5)
    self.assertEqual(self.a2, selection[0])
    self.assertEqual(self.a3, selection[1])
    self.assertEqual(self.a1, selection[2])
    self.assertEqual(self.a5, selection[3])
    self.assertEqual(self.a4, selection[4])

  def test_KeyValueSorter_numeric(self):
    sorter = KeyValueSorter(key=artefact.defaultProps.CASEINSTANCE, asNumbers=True)
    selection = sorter.sortSelection(self.data)
    self.assertEqual(len(selection), 5)
    self.assertEqual(self.a2, selection[0])
    self.assertEqual(self.a1, selection[1])
    self.assertEqual(self.a5, selection[2])
    self.assertEqual(self.a4, selection[3])
    self.assertEqual(self.a3, selection[4])

if __name__ == '__main__':
    unittest.main()