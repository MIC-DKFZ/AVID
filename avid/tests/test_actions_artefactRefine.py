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
from avid.actions.artefactRefine import ArtefactRefineBatchAction as artefactRefine
from avid.linkers import TimePointLinker

from avid.selectors.keyValueSelector import ActionTagSelector, ObjectiveSelector, TimepointSelector
from avid.common.artefact import defaultProps as artefactProps

def is_similar(reference, other, ignore_keys=None):
    rkeys = list(reference.keys())
    okeys = list(other.keys())

    if ignore_keys is None:
        ignore_keys = list()

    for key in rkeys:
        if not (key in ignore_keys) and not (reference[key] == other[key]):
            # Both have defined the property but values differ -> false
            return False
    for key in okeys:
        if not (key in ignore_keys) and not (reference[key] == other[key]):
            # Both have defined the property but values differ -> false
            return False

    return True

def custom_refinement_script(primaryInputs, outputs,**kwargs):
    '''Simple refinement.'''
    for output in outputs:
        if output[artefactProps.TIMEPOINT] == 0:
            output['baseline'] = '1';
        else:
            output['baseline'] = '0';

class TestArtefactRefineAction(unittest.TestCase):
    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "pythonActionTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "pythonActionTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_pythonAction")
      
      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)
      self.refArtefact1 = self.session.artefacts[0]
      self.refArtefact2 = self.session.artefacts[1]
      self.refArtefact3 = self.session.artefacts[2]

    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_refine_action(self):

      action = artefactRefine(ActionTagSelector("stats"), actionTag = "TestRefine")
      token = action.do()

      changedProps = [artefactProps.ACTIONTAG, artefactProps.ACTION_CLASS, artefactProps.ACTION_INSTANCE_UID,
                      artefactProps.URL, artefactProps.INPUT_IDS, artefactProps.ID, artefactProps.TIMESTAMP,
                      artefactProps.EXECUTION_DURATION]
      self.assertEqual(token.isSuccess(), True)
      result = token.generatedArtefacts[0]
      self.assertTrue(is_similar(self.refArtefact1, result, changedProps))
      self.assertEqual(result[artefactProps.ACTIONTAG], 'TestRefine')
      self.assertEqual(result[artefactProps.ACTION_CLASS], 'ArtefactRefineAction')
      result = token.generatedArtefacts[1]
      self.assertTrue(is_similar(self.refArtefact2, result, changedProps))
      self.assertEqual(result[artefactProps.ACTIONTAG], 'TestRefine')
      self.assertEqual(result[artefactProps.ACTION_CLASS], 'ArtefactRefineAction')
      result = token.generatedArtefacts[2]
      self.assertTrue(is_similar(self.refArtefact3, result, changedProps))
      self.assertEqual(result[artefactProps.ACTIONTAG], 'TestRefine')
      self.assertEqual(result[artefactProps.ACTION_CLASS], 'ArtefactRefineAction')


    def test_custom_refine_action(self):

      action = artefactRefine(ActionTagSelector("stats"), actionTag = "TestRefine", generateCallable = custom_refinement_script)
      token = action.do()

      changedProps = [artefactProps.ACTIONTAG, artefactProps.ACTION_CLASS, artefactProps.ACTION_INSTANCE_UID,
                      artefactProps.URL, artefactProps.INPUT_IDS, artefactProps.ID, artefactProps.TIMESTAMP,
                      artefactProps.EXECUTION_DURATION, 'baseline']
      self.assertEqual(token.isSuccess(), True)
      result = token.generatedArtefacts[0]
      self.assertTrue(is_similar(self.refArtefact1, result, changedProps))
      self.assertEqual(result[artefactProps.ACTIONTAG], 'TestRefine')
      self.assertEqual(result[artefactProps.ACTION_CLASS], 'ArtefactRefineAction')
      self.assertEqual(result['baseline'], '1')
      result = token.generatedArtefacts[1]
      self.assertTrue(is_similar(self.refArtefact2, result, changedProps))
      self.assertEqual(result[artefactProps.ACTIONTAG], 'TestRefine')
      self.assertEqual(result[artefactProps.ACTION_CLASS], 'ArtefactRefineAction')
      self.assertEqual(result['baseline'], '1')
      result = token.generatedArtefacts[2]
      self.assertTrue(is_similar(self.refArtefact3, result, changedProps))
      self.assertEqual(result[artefactProps.ACTIONTAG], 'TestRefine')
      self.assertEqual(result[artefactProps.ACTION_CLASS], 'ArtefactRefineAction')
      self.assertEqual(result['baseline'], '0')

if __name__ == "__main__":
    unittest.main()