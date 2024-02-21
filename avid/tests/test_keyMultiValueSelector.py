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
import avid.common.artefact as artefact
import avid.common.artefact.defaultProps as artefactProps
from avid.selectors.keyMulitValueSelector import KeyMultiValueSelector


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

  def test_KeyMultiValueSelector(self):
    selector = KeyMultiValueSelector(artefactProps.CASE, ['Case3', 'Case4', 'CaseNo'])
    selection = selector.getSelection(self.data)
    self.assertEqual(len(selection), 2)
    self.assertIn(self.a7, selection)
    self.assertIn(self.a8, selection)

    selector = KeyMultiValueSelector(artefactProps.CASE, ['CaseNo', 'CaseInExistant'])
    selection = selector.getSelection(self.data)
    self.assertEqual(len(selection), 0)

  def test_KeyMultiValueSelector_negate(self):
    selector = KeyMultiValueSelector(artefactProps.CASE, ['Case3', 'Case4'], negate=True)
    selection = selector.getSelection(self.data)
    self.assertEqual(len(selection), 6)
    self.assertIn(self.a1, selection)
    self.assertIn(self.a2, selection)
    self.assertIn(self.a3, selection)
    self.assertIn(self.a4, selection)
    self.assertIn(self.a5, selection)
    self.assertIn(self.a6, selection)

    selector = KeyMultiValueSelector(artefactProps.CASE, ['CaseNo', 'CaseInExistant'], negate=True)
    selection = selector.getSelection(self.data)
    self.assertEqual(len(selection), 8)
    self.assertIn(self.a1, selection)
    self.assertIn(self.a2, selection)
    self.assertIn(self.a3, selection)
    self.assertIn(self.a4, selection)
    self.assertIn(self.a5, selection)
    self.assertIn(self.a6, selection)
    self.assertIn(self.a7, selection)
    self.assertIn(self.a8, selection)

if __name__ == '__main__':
    unittest.main()