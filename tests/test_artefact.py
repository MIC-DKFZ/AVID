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
from avid.common import workflow
from pathlib import Path


class TestArtefact(unittest.TestCase):
  def setUp(self):
    self.a1 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action1", "result", "dummy", "myCoolFile.any")
    self.a2 = artefactGenerator.generateArtefactEntry("Case1", 1, 0, "Action2", "result", "dummy", "myCoolFile.any", "target")
    self.a3 = artefactGenerator.generateArtefactEntry("Case1", 1, 0, "IllegalChars*?", "result", "dummy", "myCoolFile.any")

    self.session = workflow.Session('TestSession', 'test_session_dir')


  def test_getArtefactShortName(self):
    name = artefact.getArtefactShortName(self.a1)
    self.assertEqual(name, 'Action1#0')
    name = artefact.getArtefactShortName(self.a2)
    self.assertEqual(name, 'Action2-target#0')
    name = artefact.getArtefactShortName(self.a3)
    self.assertEqual(name, 'IllegalChars#0')

  def test_generateArtefactPath(self):
    path = Path(artefact.generateArtefactPath(self.session, self.a1))
    expected = Path('test_session_dir') / 'TestSession' / 'Action1' / 'result' / 'Case1'
    self.assertEqual(path, expected)

    path = Path(artefact.generateArtefactPath(self.session, self.a2))
    expected = Path('test_session_dir') / 'TestSession' / 'Action2' / 'result' / 'Case1' / '1'
    self.assertEqual(path, expected)

    path = Path(artefact.generateArtefactPath(self.session, self.a3))
    expected = Path('test_session_dir') / 'TestSession' / 'IllegalChars' / 'result' / 'Case1' / '1'
    self.assertEqual(path, expected)

  def test_ensureSimilarityRelevantProperty(self):
    self.assertNotIn("ensuredTestProp", artefact.similarityRelevantProperties)
    artefact.ensureSimilarityRelevantProperty("ensuredTestProp")
    self.assertIn("ensuredTestProp", artefact.similarityRelevantProperties)

    propCount = len(artefact.similarityRelevantProperties)
    artefact.ensureSimilarityRelevantProperty("ensuredTestProp")
    self.assertEqual(propCount, len(artefact.similarityRelevantProperties))
    self.assertIn("ensuredTestProp", artefact.similarityRelevantProperties)


if __name__ == '__main__':
    unittest.main()