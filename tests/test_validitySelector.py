# SPDX-FileCopyrightText: 2024, German Cancer Research Center (DKFZ), Division of Medical Image Computing (MIC)
#
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# or find it in LICENSE.txt.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

import avid.common.artefact.generator as artefactGenerator
from avid.common.artefact import ArtefactCollection
from avid.selectors import ValiditySelector


class TestValiditySelector(unittest.TestCase):
  def setUp(self):
    self.a1 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action1", "result", "dummy", None)
    self.a2 = artefactGenerator.generateArtefactEntry("Case1", None, 1, "Action1", "result", "dummy", None)
    self.a3 = artefactGenerator.generateArtefactEntry("Case1", None, 2, "Action2", "result", "dummy", None, invalid=None)
    self.a4 = artefactGenerator.generateArtefactEntry("Case1", None, 2, "Action3", "result", "dummy", None, invalid=True)
    self.a5 = artefactGenerator.generateArtefactEntry("Case2", None, 0, "Action1", "result", "dummy", None)
    self.a6 = artefactGenerator.generateArtefactEntry("Case2", None, 1, "Action1", "result", "dummy", None, invalid=True)

    self.data = ArtefactCollection()
    self.data.add_artefact(self.a1)
    self.data.add_artefact(self.a2)
    self.data.add_artefact(self.a3)
    self.data.add_artefact(self.a4)
    self.data.add_artefact(self.a5)
    self.data.add_artefact(self.a6)

  def test_ValiditySelector(self):
    sel = ValiditySelector()
    selection = sel.getSelection(self.data)
    self.assertEqual(len(selection), 4)
    self.assertIn(self.a1, selection)
    self.assertIn(self.a2, selection)
    self.assertIn(self.a3, selection)
    self.assertIn(self.a5, selection)

  def test_ValiditySelector_negate(self):
    sel = ValiditySelector(negate=True)
    selection = sel.getSelection(self.data)
    self.assertEqual(len(selection), 2)
    self.assertIn(self.a4, selection)
    self.assertIn(self.a6, selection)

if __name__ == '__main__':
    unittest.main()