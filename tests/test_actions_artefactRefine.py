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

import avid.common.workflow as workflow
from avid.actions.artefactRefine import \
    ArtefactRefineBatchAction as artefactRefine
from avid.common.artefact import defaultProps as artefactProps
from avid.linkers import TimePointLinker
from avid.selectors.keyValueSelector import (ActionTagSelector,
                                             ObjectiveSelector,
                                             TimepointSelector)


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
            output['baseline'] = 'true'
        else:
            output['baseline'] = 'false'

class TestArtefactRefineAction(unittest.TestCase):
    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "pythonActionTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "pythonActionTest", "testlist.avid")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_pythonAction")
      
      self.session = workflow.initSession(os.path.join(self.sessionDir, "test.avid"), expandPaths=True, bootstrapArtefacts=self.testArtefactFile)

    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_simple_refine_action(self):
      selector = ActionTagSelector("stats")
      refArtefacts = selector.getSelection(self.session.artefacts)
      action = artefactRefine(selector, actionTag = "TestRefine")
      action.do()
      changedProps = [artefactProps.ACTIONTAG, artefactProps.ACTION_CLASS, artefactProps.ACTION_INSTANCE_UID,
                      artefactProps.URL, artefactProps.INPUT_IDS, artefactProps.ID, artefactProps.TIMESTAMP,
                      artefactProps.EXECUTION_DURATION]
      self.assertEqual(action.isSuccess, True)

      ref_artefact_iterator = iter(refArtefacts)
      result = action.outputArtefacts[0]
      self.assertTrue(is_similar(next(ref_artefact_iterator), result, changedProps))
      self.assertEqual(result[artefactProps.ACTIONTAG], 'TestRefine')
      self.assertEqual(result[artefactProps.ACTION_CLASS], 'ArtefactRefineAction')
      result = action.outputArtefacts[1]
      self.assertTrue(is_similar(next(ref_artefact_iterator), result, changedProps))
      self.assertEqual(result[artefactProps.ACTIONTAG], 'TestRefine')
      self.assertEqual(result[artefactProps.ACTION_CLASS], 'ArtefactRefineAction')
      result = action.outputArtefacts[2]
      self.assertTrue(is_similar(next(ref_artefact_iterator), result, changedProps))
      self.assertEqual(result[artefactProps.ACTIONTAG], 'TestRefine')
      self.assertEqual(result[artefactProps.ACTION_CLASS], 'ArtefactRefineAction')


    def test_custom_refine_action(self):
      selector = ActionTagSelector("stats")
      refArtefacts = selector.getSelection(self.session.artefacts)

      action = artefactRefine(selector, actionTag = "TestRefine", generateCallable = custom_refinement_script)
      action.do()
      changedProps = [artefactProps.ACTIONTAG, artefactProps.ACTION_CLASS, artefactProps.ACTION_INSTANCE_UID,
                      artefactProps.URL, artefactProps.INPUT_IDS, artefactProps.ID, artefactProps.TIMESTAMP,
                      artefactProps.EXECUTION_DURATION, 'baseline']
      self.assertEqual(action.isSuccess, True)

      ref_artefact_iterator = iter(refArtefacts)
      result = action.outputArtefacts[0]
      self.assertTrue(is_similar(next(ref_artefact_iterator), result, changedProps))
      self.assertEqual(result[artefactProps.ACTIONTAG], 'TestRefine')
      self.assertEqual(result[artefactProps.ACTION_CLASS], 'ArtefactRefineAction')
      self.assertEqual(result['baseline'], 'true')

      result = action.outputArtefacts[1]
      self.assertTrue(is_similar(next(ref_artefact_iterator), result, changedProps))
      self.assertEqual(result[artefactProps.ACTIONTAG], 'TestRefine')
      self.assertEqual(result[artefactProps.ACTION_CLASS], 'ArtefactRefineAction')
      self.assertEqual(result['baseline'], 'true')

      result = action.outputArtefacts[2]
      self.assertTrue(is_similar(next(ref_artefact_iterator), result, changedProps))
      self.assertEqual(result[artefactProps.ACTIONTAG], 'TestRefine')
      self.assertEqual(result[artefactProps.ACTION_CLASS], 'ArtefactRefineAction')
      self.assertEqual(result['baseline'], 'false')

if __name__ == "__main__":
    unittest.main()