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
import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact.generator as artefactGenerator
from avid.selectors import ActionTagSelector
from avid.selectors.diagnosticSelector import (IsInputSelector,
                                               IsPrimeInvalidSelector,
                                               RootSelector)
from avid.selectors.keyMulitValueSelector import KeyMultiValueSelector


class TestDiagnosticSelectors(unittest.TestCase):
    def setUp(self):
        self.data = list()
        self.data.append(artefactGenerator.generate_artefact_entry("Case1", 0, "Action1", url="no_derivatives"))
        self.data.append(artefactGenerator.generate_artefact_entry("Case1", 1, "Action1", url="derivatives"))
        self.data.append(artefactGenerator.generate_artefact_entry("Case1", 2, "Action1", url="derivatives"))
        self.data.append(artefactGenerator.generate_artefact_entry("Case2", 0, "Action1", url="derivatives"))
        self.data.append(artefactGenerator.generate_artefact_entry("Case2", 1, "Action1", url="derivatives"))
        self.data.append(artefactGenerator.generate_artefact_entry("Case3", 0, "Action1", url="no_derivatives",
                                                                   invalid=True))
        self.data.append(artefactGenerator.generate_artefact_entry("Case1", 0, "Action2", url="no_derivatives",
                                                                   **{artefactProps.INPUT_IDS: {
                                                                       'a': [self.data[1][artefactProps.ID]]}}))
        self.data.append(artefactGenerator.generate_artefact_entry("Case1", 1, "Action2", url="derivatives",
                                                                   invalid=True,
                                                                   **{artefactProps.INPUT_IDS: {
                                                                       'a': [self.data[1][artefactProps.ID]],
                                                                       'b': [self.data[2][artefactProps.ID]]}}))
        self.data.append(artefactGenerator.generate_artefact_entry("Case1", 1, "Action4", url="no_derivatives",
                                                                   invalid=True,
                                                                   **{artefactProps.INPUT_IDS: {
                                                                       'a': [self.data[7][artefactProps.ID]]}}))
        self.data.append(artefactGenerator.generate_artefact_entry("Case2", 1, "Action3", url="no_derivatives",
                                                                   **{artefactProps.INPUT_IDS: {
                                                                       'a': [self.data[3][artefactProps.ID],
                                                                             self.data[4][artefactProps.ID]]}}))

    def test_IsInputSelector(self):
        selector = IsInputSelector()

        selection = selector.getSelection(self.data)
        self.assertEqual(5, len(selection))
        self.assertIn(self.data[1], selection)
        self.assertIn(self.data[2], selection)
        self.assertIn(self.data[3], selection)
        self.assertIn(self.data[4], selection)
        self.assertIn(self.data[7], selection)

        selector = IsInputSelector(derivative_selector=ActionTagSelector("Action2"))

        selection = selector.getSelection(self.data)
        self.assertEqual(2, len(selection))
        self.assertIn(self.data[1], selection)
        self.assertIn(self.data[2], selection)

        selector = IsInputSelector(input_keys=['a'])

        selection = selector.getSelection(self.data)
        self.assertEqual(4, len(selection))
        self.assertIn(self.data[1], selection)
        self.assertIn(self.data[3], selection)
        self.assertIn(self.data[4], selection)
        self.assertIn(self.data[7], selection)

        selector = IsInputSelector(input_keys=['a'], derivative_selector=ActionTagSelector("Action2"))

        selection = selector.getSelection(self.data)
        self.assertEqual(len(selection), 1)
        self.assertIn(self.data[1], selection)

        selector = IsInputSelector(input_keys=['b'], derivative_selector=ActionTagSelector("Inexistant"))

        selection = selector.getSelection(self.data)
        self.assertEqual(len(selection), 0)

    def test_IsPrimeInvalidSelector(self):
        selector = IsPrimeInvalidSelector()
        selection = selector.getSelection(self.data)

        self.assertEqual(len(selection), 2)
        self.assertIn(self.data[5], selection)
        self.assertIn(self.data[7], selection)

    def test_RootSelector(self):
        selector = RootSelector()
        selection = selector.getSelection(self.data)

        self.assertEqual(len(selection), 6)
        self.assertIn(self.data[0], selection)
        self.assertIn(self.data[1], selection)
        self.assertIn(self.data[2], selection)
        self.assertIn(self.data[3], selection)
        self.assertIn(self.data[4], selection)
        self.assertIn(self.data[5], selection)


if __name__ == '__main__':
    unittest.main()
