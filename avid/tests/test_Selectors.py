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
from avid.selectors import AndSelector, OrSelector, KeyValueSelector
from avid.selectors import ActionTagSelector
from avid.selectors import CaseSelector
from avid.selectors import ValidResultSelector

class TestSelectors(unittest.TestCase):
  def setUp(self):
    self.a1 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action1", "result", "dummy", None)
    self.a2 = artefactGenerator.generateArtefactEntry("Case1", None, 1, "Action1", "result", "dummy", None)
    self.a3 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action2", "result", "dummy", None)
    self.a4 = artefactGenerator.generateArtefactEntry("Case2", None, 0, "Action1", "result", "dummy", None)
    self.a5 = artefactGenerator.generateArtefactEntry("Case2", None, 1, "Action1", "result", "dummy", None)
    self.a6 = artefactGenerator.generateArtefactEntry("Case2", None, 0, "Action2", "result", "dummy", None)
    self.a7 = artefactGenerator.generateArtefactEntry("Case3", "a", 0, "Action2", "result", "dummy", None)
    self.a8 = artefactGenerator.generateArtefactEntry("Case4", "1", 0, "Action3", "result", "dummy", None)

    self.data = list()
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a1)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a2)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a3)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a4)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a5)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a6)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a7)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a8)

    self.a9 = artefactGenerator.generateArtefactEntry("Case3", "a", 0, "Action2", "config", "dummy", None)
    self.a10 = artefactGenerator.generateArtefactEntry("Case4", "1", 0, "Action3", "result", "dummy", invalid=True)
    self.data2 = list()
    self.data2 = artefact.addArtefactToWorkflowData(self.data2, self.a1)
    self.data2 = artefact.addArtefactToWorkflowData(self.data2, self.a2)
    self.data2 = artefact.addArtefactToWorkflowData(self.data2, self.a3)
    self.data2 = artefact.addArtefactToWorkflowData(self.data2, self.a9)
    self.data2 = artefact.addArtefactToWorkflowData(self.data2, self.a10)

  def test_KeyValueSelector(self):
    selector = KeyValueSelector("timePoint", 0)
    selection = selector.getSelection(self.data)
    self.assertEqual(len(selection), 6)
    self.assertIn(self.a1, selection)
    self.assertIn(self.a3, selection)
    self.assertIn(self.a4, selection)
    self.assertIn(self.a6, selection)
    self.assertIn(self.a7, selection)
    self.assertIn(self.a8, selection)

  def test_KeyValueSelector_negate(self):
    selector = KeyValueSelector("timePoint", 0, negate=True)
    selection = selector.getSelection(self.data)
    self.assertEqual(len(selection), 2)
    self.assertIn(self.a2, selection)
    self.assertIn(self.a5, selection)

  def test_KeyValueSelector_allowstring(self):
    selector = KeyValueSelector("timePoint", "0")
    selection = selector.getSelection(self.data)
    self.assertEqual(len(selection), 0)

    selector = KeyValueSelector("timePoint", "0", allowStringCompare=True)
    selection = selector.getSelection(self.data)
    self.assertEqual(len(selection), 6)
    self.assertIn(self.a1, selection)
    self.assertIn(self.a3, selection)
    self.assertIn(self.a4, selection)
    self.assertIn(self.a6, selection)
    self.assertIn(self.a7, selection)
    self.assertIn(self.a8, selection)

  def test_KeyValueSelector_allowstring_negate(self):
    selector = KeyValueSelector("timePoint", "0", negate = True)
    selection = selector.getSelection(self.data)
    self.assertEqual(len(selection), 8)

    selector = KeyValueSelector("timePoint", "0", allowStringCompare=True, negate = True)
    selection = selector.getSelection(self.data)
    self.assertEqual(len(selection), 2)
    self.assertIn(self.a2, selection)
    self.assertIn(self.a5, selection)

  def test_ActionTagSelector(self):
    selector = ActionTagSelector("Action1")
    selection = selector.getSelection(self.data)
    self.assertEqual(len(selection), 4)
    self.assertIn(self.a1, selection)
    self.assertIn(self.a2, selection)
    self.assertIn(self.a4, selection)
    self.assertIn(self.a5, selection)
    
  def test_ActionTagSelector_negate(self):
    selector = ActionTagSelector("Action1", negate=True)
    selection = selector.getSelection(self.data)
    self.assertEqual(len(selection), 4)
    self.assertIn(self.a3, selection)
    self.assertIn(self.a6, selection)
    self.assertIn(self.a7, selection)
    self.assertIn(self.a8, selection)

  def test_CaseSelector(self):
    selector = CaseSelector("Case3")
    selection = selector.getSelection(self.data)
    self.assertEqual(len(selection), 1)
    self.assertIn(self.a7, selection)

  def test_CaseSelector_negate(self):
    selector = CaseSelector("Case3", True)
    selection = selector.getSelection(self.data)
    self.assertEqual(len(selection), 7)
    self.assertIn(self.a1, selection)
    self.assertIn(self.a2, selection)
    self.assertIn(self.a3, selection)
    self.assertIn(self.a4, selection)
    self.assertIn(self.a5, selection)
    self.assertIn(self.a6, selection)
    self.assertIn(self.a8, selection)

  def test_AndSelector(self):
    selector = ActionTagSelector("Action1") + CaseSelector("Case2")
    selection = selector.getSelection(self.data)
    self.assertEqual(len(selection), 2)
    self.assertIn(self.a4, selection)
    self.assertIn(self.a5, selection)
  
    selector2 = AndSelector(ActionTagSelector("Action1"), CaseSelector("Case2"))
    selection = selector2.getSelection(self.data)
    self.assertEqual(len(selection), 2)
    self.assertIn(self.a4, selection)
    self.assertIn(self.a5, selection)

  def test_OrSelector(self):
    selector = OrSelector(ActionTagSelector("Action1"), CaseSelector("Case2"))
    selection = selector.getSelection(self.data)
    self.assertEqual(len(selection), 5)
    self.assertIn(self.a1, selection)
    self.assertIn(self.a2, selection)
    self.assertIn(self.a4, selection)
    self.assertIn(self.a5, selection)
    self.assertIn(self.a6, selection)

  def test_ValidResultSelector(self):
    selector = ValidResultSelector()
    selection = selector.getSelection(self.data2)
    self.assertEqual(len(selection), 3)
    self.assertIn(self.a1, selection)
    self.assertIn(self.a2, selection)
    self.assertIn(self.a3, selection)
  

if __name__ == '__main__':
    unittest.main()