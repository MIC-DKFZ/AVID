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

import avid.common.artefact as artefact
import avid.common.artefact.generator as artefactGenerator
from avid.linkers import AndLinker, CaseLinker, LinkerBase, TimePointLinker


class TestLinkers(unittest.TestCase):
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

  def test_LinkerBase(self):
    linker = LinkerBase()
    selection = linker.getLinkedSelection(2, self.data, self.data)
    self.assertEqual(selection, self.data)

    selection = linker.getLinkedSelection(0, self.data, self.data)
    self.assertEqual(selection, self.data)


  def test_AndLinker(self):
    linker = CaseLinker() + TimePointLinker()
    selections = linker.getLinkedSelection(2, self.data,self.data)
    self.assertEqual(len(selections), 2)
    self.assertEqual(len(selections[0]), 1)
    self.assertEqual(len(selections[1]), 1)
    self.assertIn(self.a3, selections[0])
    self.assertIn(self.a4, selections[1])
  
    selections = linker.getLinkedSelection(0, self.data,self.data)
    self.assertEqual(len(selections), 1)
    self.assertEqual(len(selections[0]), 1)
    self.assertIn(self.a1, selections[0])
    
    selector2 = AndLinker(CaseLinker(), TimePointLinker())
    selections = selector2.getLinkedSelection(2, self.data,self.data)
    self.assertEqual(len(selections), 2)
    self.assertEqual(len(selections[0]), 1)
    self.assertEqual(len(selections[1]), 1)
    self.assertIn(self.a3, selections[0])
    self.assertIn(self.a4, selections[1])


if __name__ == '__main__':
    unittest.main()