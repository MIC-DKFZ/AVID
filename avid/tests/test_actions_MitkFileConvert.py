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
import os
import shutil
import avid.common.workflow as workflow
from avid.actions.MitkFileConverter import MitkFileConverterBatchAction as convert
from avid.selectors.keyValueSelector import ActionTagSelector

from avid.common.AVIDUrlLocater import getExecutableURL
import avid.common.artefact.defaultProps as artefactProps

@unittest.skipIf(getExecutableURL(None, 'MitkFileConverter') is None, 'Tool MitkFileConverter not installed on the system.')
class TestMitkFileConverter(unittest.TestCase):

    def setUp(self):
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "MitkFileConverterTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_MitkFileConvert")

      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)


    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_convert_action(self):

      action = convert(inputSelector=ActionTagSelector("Simple"), actionTag = "TestConvert")
      token = action.do()

      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSkipped(), True)

      action = convert(ActionTagSelector("Simple"), defaultoutputextension='nii',
                      actionTag="TestConvert2")
      token = action.do()

      self.assertEqual(token.isSuccess(), True)

    def test_simple_convert_action_alwaysdo(self):

      action = convert(inputSelector=ActionTagSelector("Simple"), actionTag = "TestConvertAlwaysDo", alwaysDo=True)
      token = action.do()

      self.assertEqual(token.isSuccess(), True)

      token = action.do()
      self.assertEqual(token.isSuccess(), True)

    def test_splitting_convert_action(self):

      action = convert(inputSelector=ActionTagSelector("Splitting"), actionTag = "TestConvertSplitting")
      token = action.do()

      self.assertEqual(token.isSuccess(), True)
      self.assertEqual(len(token.generatedArtefacts), 3)
      self.assertEqual(token.generatedArtefacts[0][artefactProps.RESULT_SUB_TAG], '0')
      self.assertEqual(token.generatedArtefacts[1][artefactProps.RESULT_SUB_TAG], '1')
      self.assertEqual(token.generatedArtefacts[2][artefactProps.RESULT_SUB_TAG], '2')


if __name__ == "__main__":
    unittest.main()
