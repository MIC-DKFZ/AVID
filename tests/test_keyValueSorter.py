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
from avid.common.artefact import ArtefactCollection, defaultProps
from avid.sorter import KeyValueSorter


class TestKeyValueSorter(unittest.TestCase):
    def setUp(self):
        self.a1 = artefactGenerator.generateArtefactEntry(
            "Case3", "3", 0, "Action1", "result", "dummy", None
        )
        self.a2 = artefactGenerator.generateArtefactEntry(
            "Case5", "1", 1, "Action1", "result", "dummy", None
        )
        self.a3 = artefactGenerator.generateArtefactEntry(
            "Case1", "20", 0, "Action2", "result", "dummy", None
        )
        self.a4 = artefactGenerator.generateArtefactEntry(
            "Case2", "7", 0, "Action1", "result", "dummy", None
        )
        self.a5 = artefactGenerator.generateArtefactEntry(
            "Case4", "5", 1, "Action1", "result", "dummy", None
        )

        self.data = ArtefactCollection()
        self.data.add_artefact(self.a1)
        self.data.add_artefact(self.a2)
        self.data.add_artefact(self.a3)
        self.data.add_artefact(self.a4)
        self.data.add_artefact(self.a5)

    def test_KeyValueSorter(self):
        sorter = KeyValueSorter(key=defaultProps.CASE)
        selection = sorter.sortSelection(self.data)
        sel_iter = iter(selection)

        self.assertEqual(len(selection), 5)
        self.assertEqual(self.a3, next(sel_iter))
        self.assertEqual(self.a4, next(sel_iter))
        self.assertEqual(self.a1, next(sel_iter))
        self.assertEqual(self.a5, next(sel_iter))
        self.assertEqual(self.a2, next(sel_iter))

        sorter = KeyValueSorter(key=defaultProps.CASEINSTANCE)
        selection = sorter.sortSelection(self.data)
        sel_iter = iter(selection)

        self.assertEqual(len(selection), 5)
        self.assertEqual(self.a2, next(sel_iter))
        self.assertEqual(self.a3, next(sel_iter))
        self.assertEqual(self.a1, next(sel_iter))
        self.assertEqual(self.a5, next(sel_iter))
        self.assertEqual(self.a4, next(sel_iter))

    def test_KeyValueSorter_numeric(self):
        sorter = KeyValueSorter(key=defaultProps.CASEINSTANCE, asNumbers=True)
        selection = sorter.sortSelection(self.data)
        sel_iter = iter(selection)

        self.assertEqual(len(selection), 5)
        self.assertEqual(self.a2, next(sel_iter))
        self.assertEqual(self.a1, next(sel_iter))
        self.assertEqual(self.a5, next(sel_iter))
        self.assertEqual(self.a4, next(sel_iter))
        self.assertEqual(self.a3, next(sel_iter))


if __name__ == "__main__":
    unittest.main()
