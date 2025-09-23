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
from avid.selectors import (
    ActionTagSelector,
    AndSelector,
    CaseSelector,
    KeyValueSelector,
    OrSelector,
    ValidResultSelector,
)


class TestSelectors(unittest.TestCase):
    def setUp(self):
        self.a1 = artefactGenerator.generateArtefactEntry(
            "Case1", None, 0, "Action1", "result", "dummy", None
        )
        self.a2 = artefactGenerator.generateArtefactEntry(
            "Case1", None, 1, "Action1", "result", "dummy", None
        )
        self.a3 = artefactGenerator.generateArtefactEntry(
            "Case1", None, 0, "Action2", "result", "dummy", None
        )
        self.a4 = artefactGenerator.generateArtefactEntry(
            "Case2", None, 0, "Action1", "result", "dummy", None
        )
        self.a5 = artefactGenerator.generateArtefactEntry(
            "Case2", None, 1, "Action1", "result", "dummy", None
        )
        self.a6 = artefactGenerator.generateArtefactEntry(
            "Case2", None, 0, "Action2", "result", "dummy", None
        )
        self.a7 = artefactGenerator.generateArtefactEntry(
            "Case3", "a", 0, "Action2", "result", "dummy", None
        )
        self.a8 = artefactGenerator.generateArtefactEntry(
            "Case4", "1", 0, "Action3", "result", "dummy", None
        )

        self.data = artefact.ArtefactCollection()
        self.data.add_artefact(self.a1)
        self.data.add_artefact(self.a2)
        self.data.add_artefact(self.a3)
        self.data.add_artefact(self.a4)
        self.data.add_artefact(self.a5)
        self.data.add_artefact(self.a6)
        self.data.add_artefact(self.a7)
        self.data.add_artefact(self.a8)

        self.a9 = artefactGenerator.generateArtefactEntry(
            "Case3", "a", 0, "Action2", "config", "dummy", None
        )
        self.a10 = artefactGenerator.generateArtefactEntry(
            "Case4", "1", 0, "Action3", "result", "dummy", invalid=True
        )
        self.data2 = artefact.ArtefactCollection()
        self.data2.add_artefact(self.a1)
        self.data2.add_artefact(self.a2)
        self.data2.add_artefact(self.a3)
        self.data2.add_artefact(self.a9)
        self.data2.add_artefact(self.a10)

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
        selector = KeyValueSelector("timePoint", "0", negate=True)
        selection = selector.getSelection(self.data)
        self.assertEqual(len(selection), 8)

        selector = KeyValueSelector(
            "timePoint", "0", allowStringCompare=True, negate=True
        )
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


if __name__ == "__main__":
    unittest.main()
