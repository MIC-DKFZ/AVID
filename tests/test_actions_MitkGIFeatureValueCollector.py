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

import os
import shutil
import unittest

import avid.common.artefact.defaultProps as artefactProps
import avid.common.workflow as workflow
from avid.actions.mitk.MitkGIFeatureValueCollector import \
    MitkGIFeatureValueCollectorBatchAction as collector
from avid.selectors.keyValueSelector import ActionTagSelector
from avid.splitter import KeyValueSplitter


class MitkGIFeatureValueCollector(unittest.TestCase):


    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "MitkGIFeatureValueCollectorTest")
      self.testSmallArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "MitkGIFeatureValueCollectorTest", "testlist_small.avid")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "MitkGIFeatureValueCollectorTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary","test_MitkGIFeatureValueCollector")
      self.tempRoot = os.path.join(os.path.split(__file__)[0],"temporary")

              
    def tearDown(self):
      try:
        shutil.rmtree(self.tempRoot)
      except:
        pass


    def readFile(self, filePath):
      result = None
      with open(filePath) as fileHandle:
        result = fileHandle.read()
        
      return result


    def test_simple_batch_action(self):
      session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testSmallArtefactFile)

      action = collector(ActionTagSelector('GIF'))
      action.do()
      self.assertEqual(action.isSuccess, True)

      #refFile = os.path.join(self.testDataDir, "ref_simple_small_values.csv")
      #resultFile = artefactHelper.getArtefactProperty(action._actions[0].outputArtefacts[0], artefactProps.URL)
      #self.assertEqual(self.readFile(refFile), self.readFile(resultFile))


      action = collector(feature_selector=ActionTagSelector('GIF'),selected_features = ['Mean'], value_table = False,
                         column_key = artefactProps.OBJECTIVE)
      action.do()
      self.assertEqual(action.isSuccess, True)


    def test_batch_action(self):
        session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

        action = collector(ActionTagSelector('GIF'), row_keys = [artefactProps.CASE, artefactProps.OBJECTIVE, artefactProps.TIMEPOINT])
        action.do()
        self.assertEqual(action.isSuccess, True)

        #refFile = os.path.join(self.testDataDir, "ref_simple_small_values.csv")
        #resultFile = artefactHelper.getArtefactProperty(action._actions[0].outputArtefacts[0], artefactProps.URL)
        #self.assertEqual(self.readFile(refFile), self.readFile(resultFile))


        action = collector(feature_selector=ActionTagSelector('GIF'),selected_features = ['Mean'], value_table = False,
                           row_keys = [artefactProps.CASE, artefactProps.TIMEPOINT], column_key = artefactProps.OBJECTIVE)
        action.do()
        self.assertEqual(action.isSuccess, True)

        action = collector(feature_selector=ActionTagSelector('GIF'), feature_splitter=KeyValueSplitter(artefactProps.OBJECTIVE),
                           selected_features = ['Mean'], value_table = False,
                           row_keys = [artefactProps.CASE], column_key = artefactProps.TIMEPOINT)
        action.do()
        self.assertEqual(action.isSuccess, True)


if __name__ == "__main__":
    unittest.main()