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
from avid.actions.mitk.MitkSplit4Dto3DImages import MitkSplit4Dto3DImagesBatchAction as split
from avid.actions.mitk.MitkSplit4Dto3DImages import MitkSplit4Dto3DImagesAction as SplitAction
from avid.selectors.keyValueSelector import ActionTagSelector
from avid.common.AVIDUrlLocater import getExecutableURL
import avid.common.artefact.defaultProps as artefacProps

@unittest.skipIf(getExecutableURL(None,'MitkSplit4Dto3DImages') is None, 'Tool MitkSplit4Dto3DImages is not installed on the system.')
class TestMitkMRPerfusionMiniApp(unittest.TestCase):

    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "MRPerfusionMiniAppTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "MRPerfusionMiniAppTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_MitkSplit4Dto3DImages")
      
      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_split_action(self):
      
      action = split(ActionTagSelector("Signal"), actionTag = "TestSplit")
      action.do()
                    
      self.assertEqual(action.isSuccess, True)
      self.assertEqual(len(action.outputArtefacts), 10)
      for index, output in enumerate(action.outputArtefacts):
        self.assertEqual(action.outputArtefacts[index][SplitAction.PROPERTY_ORIGINAL_TIME_STEP], str(index))
        self.assertEqual(action.outputArtefacts[index][artefacProps.RESULT_SUB_TAG], str(index))
        self.assertEqual(action.outputArtefacts[index][SplitAction.PROPERTY_DYNAMIC_SOURCE], action.outputArtefacts[index][artefacProps.INPUT_IDS]['i'][0])


if __name__ == "__main__":
    unittest.main()