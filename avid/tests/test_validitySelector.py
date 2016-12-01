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
from avid.selectors import ValiditySelector

class TestValiditySelector(unittest.TestCase):
  def setUp(self):
    self.a1 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action1", "result", "dummy", None)
    self.a2 = artefactGenerator.generateArtefactEntry("Case1", None, 1, "Action1", "result", "dummy", None)
    self.a3 = artefactGenerator.generateArtefactEntry("Case1", None, 2, "Action2", "result", "dummy", None, invalid=None)
    self.a4 = artefactGenerator.generateArtefactEntry("Case1", None, 2, "Action3", "result", "dummy", None, invalid=True)
    self.a5 = artefactGenerator.generateArtefactEntry("Case2", None, 0, "Action1", "result", "dummy", None)
    self.a6 = artefactGenerator.generateArtefactEntry("Case2", None, 1, "Action1", "result", "dummy", None, invalid=True)

    self.data = list()
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a1)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a2)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a3)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a4)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a5)
    self.data = artefact.addArtefactToWorkflowData(self.data, self.a6)

  def test_ValiditySelector(self):
    sel = ValiditySelector()
    selection = sel.getSelection(self.data)
    self.assertEqual(len(selection), 4)
    self.assertIn(self.a1, selection)
    self.assertIn(self.a2, selection)
    self.assertIn(self.a3, selection)
    self.assertIn(self.a5, selection) 

if __name__ == '__main__':
    unittest.main()