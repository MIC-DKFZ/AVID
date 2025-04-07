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
from avid.common.artefact import ArtefactCollection, ensureCaseInstanceValidity
import avid.common.artefact.defaultProps as artefactProps

class TestArtefactGeneration(unittest.TestCase):
  def setUp(self):
    self.a1 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action1", "result", "dummy", "myCoolFile.any")
    self.a2 = artefactGenerator.generateArtefactEntry("Case2", 1, 0, "Action1", "misc", "dummy", None, "Head", True, customProp1 = "nice", customProp2 = 42)
    self.a3 = artefactGenerator.generateArtefactEntry("Case3", "a", 0, "Action2", "result", "dummy", None, None, False)
    self.a4 = artefactGenerator.generateArtefactEntry("Case4", "1", 0, "Action3", "result", "dummy", None)
    self.a5 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action1", "result", "dummy", "myCoolFileVersion2.any")
    self.a6 = artefactGenerator.generateArtefactEntry("Case1", 1, 0, "Action2", "result", "dummy", "myCoolFileVersion2.any")

    self.data = ArtefactCollection()
    self.data.add_artefact(self.a1)
    self.data.add_artefact(self.a2)
    self.data.add_artefact(self.a3)

  def test_generateArtefactEntry(self):
    self.assertEqual(self.a1[artefactProps.CASE], "Case1")
    self.assertEqual(self.a1[artefactProps.CASEINSTANCE], None)
    self.assertEqual(self.a1[artefactProps.TIMEPOINT], 0)
    self.assertEqual(self.a1[artefactProps.ACTIONTAG], "Action1")
    self.assertEqual(self.a1[artefactProps.TYPE], "result")
    self.assertEqual(self.a1[artefactProps.FORMAT], "dummy")
    self.assertEqual(self.a1[artefactProps.URL], "myCoolFile.any")
    self.assertEqual(self.a1[artefactProps.OBJECTIVE], None)
    self.assertEqual(self.a1[artefactProps.INVALID], False)
    self.assertEqual(self.a1[artefactProps.INPUT_IDS], None)

    self.assertEqual(self.a2["customProp1"], "nice")
    self.assertEqual(self.a2["customProp2"], "42")
    self.assertEqual(self.a2[artefactProps.OBJECTIVE], "Head")
    self.assertEqual(self.a2[artefactProps.INVALID], True)
    

  def test_addArtefactToWorkflowData(self):
    workflowData = ArtefactCollection()
    workflowData.add_artefact(self.a1)
    workflowData.add_artefact(self.a3)
    
    self.assertEqual(len(workflowData), 2)
    self.assertIn(self.a1, workflowData)
    self.assertIn(self.a3, workflowData)
    
    #Check remove simelar is active
    workflowData.add_artefact(self.a5, True)
    self.assertEqual(len(workflowData), 2)
    self.assertIn(self.a3, workflowData)
    self.assertIn(self.a5, workflowData)

    #Check remove simelar is inactive
    self.assertRaises(ValueError, workflowData.add_artefact, self.a1, False)

  def test_findSimelarArtefact(self):
    self.assertEqual(self.data.find_similar(self.a1), self.a1)
    self.assertEqual(self.data.find_similar(self.a2), self.a2)
    self.assertEqual(self.data.find_similar(self.a4), None)
    self.assertEqual(self.data.find_similar(self.a5), self.a1, "Check if it finds artefact that are only different by URL and returns them")
    
  def test_artefactExists(self):
    self.assertEqual(self.data.similar_artefact_exists(self.a1), True)
    self.assertEqual(self.data.similar_artefact_exists(self.a2), True)
    self.assertEqual(self.data.similar_artefact_exists(self.a4), False)
    self.assertEqual(self.data.similar_artefact_exists(self.a5), True, "Check if it finds artefact that are only different by URL and returns them")

    self.assertEqual(self.data.identical_artefact_exists(self.a1), True)
    self.assertEqual(self.data.identical_artefact_exists(self.a2), True)
    self.assertEqual(self.data.identical_artefact_exists(self.a4), False)
    self.assertEqual(self.data.identical_artefact_exists(self.a5), False, "Check if it finds artefact that are only different by URL and returns them")

    self.assertTrue(self.a1 in self.data)
    self.assertTrue(self.a2 in self.data)
    self.assertTrue(self.a4 not in self.data)
    self.assertTrue(self.a5 not in self.data)

  def test_ensureCaseInstanceValidity(self):
    testA = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action1", "result", "dummy", "myCoolFile.any")
    result = ensureCaseInstanceValidity(testA, self.a1, self.a5)
    
    self.assertEqual(result, True)
    self.assertEqual(testA[artefactProps.CASEINSTANCE], None)
    
    result = ensureCaseInstanceValidity(testA, self.a1, self.a2, self.a5, None)
    
    self.assertEqual(result, True)
    self.assertEqual(testA[artefactProps.CASEINSTANCE], self.a2[artefactProps.CASEINSTANCE])

    #conflict due to different instance testA and self.a3
    result = ensureCaseInstanceValidity(testA, self.a1, self.a3)
    
    self.assertEqual(result, False)
    self.assertEqual(testA[artefactProps.CASEINSTANCE], self.a2[artefactProps.CASEINSTANCE])

    #conflict due to different instance self.a2 and self.a3
    testA = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action1", "result", "dummy", "myCoolFile.any")
    result = ensureCaseInstanceValidity(testA, self.a2, self.a3)
    
    self.assertEqual(result, False)
    self.assertEqual(testA[artefactProps.CASEINSTANCE], self.a2[artefactProps.CASEINSTANCE])
    

if __name__ == '__main__':
    unittest.main()