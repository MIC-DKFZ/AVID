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
from pathlib import Path

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact.generator as artefactGenerator
import avid.common.workflow as workflow
from avid.actions.genericCLIAction import GenericCLIAction, generate_cli_call


def generateNameCallableAlternative(actionInstance, **allActionArgs):
    return 'test_{}_{}'.format(actionInstance._actionTag, actionInstance._actionID)


class Test(unittest.TestCase):

    def checkSelections(self, refSelections, testSelections):
        self.assertEqual(len(testSelections), len(refSelections))

        for pos, refSelection in enumerate(refSelections):
            self.assertEqual(len(testSelections[pos]), len(refSelection))
            for posArtefact, artefact in enumerate(refSelection):
                self.assertIn(artefact, testSelections[pos])

    def getURL(self, a):
        return a[artefactProps.URL]

    def setUp(self):
        self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_actions")
        self.testDataDir = os.path.join(os.path.split(__file__)[0],"data")

        self.a1 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action1", artefactProps.TYPE_VALUE_RESULT, "dummy", os.path.join(self.testDataDir, "a1.txt"))
        self.a2 = artefactGenerator.generateArtefactEntry("Case1", None, 1, "Action1", artefactProps.TYPE_VALUE_RESULT, "dummy", os.path.join(self.testDataDir, "a2.txt"))
        self.a3 = artefactGenerator.generateArtefactEntry("Case2", None, 2, "Action1", artefactProps.TYPE_VALUE_RESULT, "dummy", os.path.join(self.testDataDir, "a3.txt"))
        self.a4 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action2", artefactProps.TYPE_VALUE_RESULT, "dummy", os.path.join(self.testDataDir, "a4.txt"))

        self.session = workflow.Session("session1", self.sessionDir)
        self.session.setWorkflowActionTool('TestCLI', 'test.exe')

    def tearDown(self):
        try:
            shutil.rmtree(self.sessionDir)
        except:
            pass

    def test_generate_cli_call(self):
        ref = '"cli.exe" -i "{}" "{}"'.format(self.getURL(self.a1), self.getURL(self.a2))
        call = generate_cli_call(exec_url="cli.exe", artefact_args={'i': [self.a1,self.a2]}, additional_args=None,
                                 arg_positions=None)
        self.assertEqual(ref, call)

        ref = '"cli.exe" -i "{}" -a "A" --bb "BB" -c "C"'.format(self.getURL(self.a1))
        call = generate_cli_call(exec_url="cli.exe", artefact_args={'i': [self.a1]},
                                 additional_args={'a': 'A', 'bb': 'BB', 'c': 'C'}, arg_positions=None)
        self.assertEqual(ref, call)

        ref = '"cli.exe" -i "{}" "{}" --out "{}" -a "A" --bb "BB" -c "C"'.format(self.getURL(self.a1),
                                                                                 self.getURL(self.a2),
                                                                                 self.getURL(self.a3))
        call = generate_cli_call(exec_url="cli.exe", artefact_args={'i': [self.a1,self.a2], 'out': [self.a3]},
                                 additional_args={'a': 'A', 'bb': 'BB', 'c': 'C'}, arg_positions=None)
        self.assertEqual(ref, call)

        ref = '"cli.exe" -i "{}" -a "A" --bb "BB" -c "C"'.format(self.getURL(self.a1))
        call = generate_cli_call(exec_url="cli.exe", artefact_args={'i': [self.a1, None], 'out': [None]},
                                 additional_args={'a': 'A', 'bb': 'BB', 'c': 'C'}, arg_positions=None)
        self.assertEqual(ref, call)

        ref = '"cli.exe" "{}" "{}" "BB" --out "{}" -a "A" -c "C"'.format(self.getURL(self.a1),self.getURL(self.a2),
                                                                         self.getURL(self.a3))
        call = generate_cli_call(exec_url="cli.exe", artefact_args={'i': [self.a1,self.a2], 'out': [self.a3]},
                                 additional_args={'a': 'A', 'bb': 'BB', 'c': 'C'}, arg_positions=['i', 'bb'])
        self.assertEqual(ref, call)

        ref = '"cli.exe" "C" "{}" "{}" "{}" -a "A" --bb "BB" --None'.format(self.getURL(self.a3),self.getURL(self.a1),
                                                                            self.getURL(self.a2))
        call = generate_cli_call(exec_url="cli.exe", artefact_args={'i': [self.a1,self.a2], 'out': [self.a3]},
                                 additional_args={'a': 'A', 'bb': 'BB', 'c': 'C', 'None': None},
                                 arg_positions=['c', 'out', 'i', 'unkown_arg'])
        self.assertEqual(ref, call)

        ref = '"cli.exe"'
        call = generate_cli_call(exec_url="cli.exe", artefact_args={'i': None}, additional_args=None, arg_positions=None)
        self.assertEqual(ref, call)

    def test_GenericCLIAction(self):
        action = GenericCLIAction(tool_id="TestCLI", input=[self.a1], session=self.session)

        outputs = action.outputArtefacts
        self.assertEqual('Case1',outputs[0][artefactProps.CASE])
        self.assertEqual('GenericCLI',outputs[0][artefactProps.ACTIONTAG])
        filename = Path(outputs[0][artefactProps.URL]).stem
        self.assertTrue(filename.startswith('TestCLI_GenericCLI'))

        call = action._prepareCLIExecution()
        ref = '"test.exe" "{}" --input "{}"'.format(self.getURL(outputs[0]),self.getURL(self.a1))
        self.assertEqual(ref,call)

        action = GenericCLIAction(tool_id="TestCLI", input=[self.a1], session=self.session,
                                  generateNameCallable=generateNameCallableAlternative)
        outputs = action.outputArtefacts
        filename = Path(outputs[0][artefactProps.URL]).stem
        self.assertTrue(filename.startswith('test_GenericCLI_TestCLI'))

        action = GenericCLIAction(tool_id="TestCLI", input=[self.a1], x=[self.a2, self.a3], outputFlags=['out'],
                                  session=self.session)
        outputs = action.outputArtefacts
        call = action._prepareCLIExecution()
        ref = '"test.exe" --input "{}" -x "{}" "{}" --out "{}"'.format(self.getURL(self.a1),self.getURL(self.a2),
                                                                      self.getURL(self.a3),self.getURL(outputs[0]))
        self.assertEqual(ref,call)
        self.assertEqual(outputs[0][artefactProps.TIMEPOINT],0, msg='Timpoint of output should be 0 because "input" should be used as default ref (picked by alphabetic order.')

        action = GenericCLIAction(tool_id="TestCLI", input=[self.a1], x=[self.a2, self.a3], outputFlags=['out'],
                                  outputReferenceArtefactName='x', session=self.session)
        outputs = action.outputArtefacts
        call = action._prepareCLIExecution()
        ref = '"test.exe" --input "{}" -x "{}" "{}" --out "{}"'.format(self.getURL(self.a1),self.getURL(self.a2),
                                                                       self.getURL(self.a3),self.getURL(outputs[0]))
        self.assertEqual(ref,call)
        self.assertEqual(outputs[0][artefactProps.TIMEPOINT],1, msg='Timpoint of output should be 1 because "x" was indicated as ref.')

        action = GenericCLIAction(tool_id="TestCLI", input=[self.a1], x=[self.a2, self.a3], outputFlags=['out'],
                                  noOutputArgs=True, session=self.session)
        call = action._prepareCLIExecution()
        ref = '"test.exe" --input "{}" -x "{}" "{}"'.format(self.getURL(self.a1),self.getURL(self.a2),
                                                                       self.getURL(self.a3))
        self.assertEqual(ref,call)

        action = GenericCLIAction(tool_id="TestCLI", additionalArgs={'a': 'A', 'bb': 'BB'}, input=[self.a1],
                                  x=[self.a2, self.a3], outputFlags=['o'], session=self.session)
        outputs = action.outputArtefacts
        call = action._prepareCLIExecution()
        ref = '"test.exe" --input "{}" -x "{}" "{}" -o "{}" -a "A" --bb "BB"'.format(self.getURL(self.a1),self.getURL(self.a2),
                                                                      self.getURL(self.a3),self.getURL(outputs[0]))
        self.assertEqual(ref,call)

        action = GenericCLIAction(tool_id="TestCLI", additionalArgs={'a': 'A', 'bb': 'BB'}, input=[self.a1],
                                  x=[self.a2, self.a3], outputFlags=['o'], illegalArgs=['not_existant'], session=self.session)
        outputs = action.outputArtefacts
        call = action._prepareCLIExecution()
        ref = '"test.exe" --input "{}" -x "{}" "{}" -o "{}" -a "A" --bb "BB"'.format(self.getURL(self.a1),self.getURL(self.a2),
                                                                      self.getURL(self.a3),self.getURL(outputs[0]))
        self.assertEqual(ref,call)

        action = GenericCLIAction(tool_id="TestCLI", additionalArgs={'a': 'A', 'bb': 'BB'}, input=[self.a1],
                                  x=[self.a2, self.a3], outputFlags=['o'], argPositions=['o','bb','input'],
                                  session=self.session)
        outputs = action.outputArtefacts
        call = action._prepareCLIExecution()
        ref = '"test.exe" "{}" "BB" "{}" -x "{}" "{}" -a "A"'.format(self.getURL(outputs[0]), self.getURL(self.a1),
                                                                   self.getURL(self.a2), self.getURL(self.a3))
        self.assertEqual(ref,call)

        action = GenericCLIAction(tool_id="TestCLI", additionalArgs={'a': 'A', 'bb': 'BB'}, input=[self.a1],
                                  x=[self.a2, self.a3], outputFlags=['o'], argPositions=['o','bb','input'],
                                  noOutputArgs=True, session=self.session)
        outputs = action.outputArtefacts
        call = action._prepareCLIExecution()
        ref = '"test.exe" "BB" "{}" -x "{}" "{}" -a "A"'.format(self.getURL(self.a1), self.getURL(self.a2),
                                                              self.getURL(self.a3))
        self.assertEqual(ref,call)

        #invalid inputs
        self.assertRaises(ValueError, GenericCLIAction, tool_id="TestCLI", input=None, session=self.session)
        #no inputs
        self.assertRaises(RuntimeError, GenericCLIAction, tool_id="TestCLI", session=self.session)
        #illegal inputs cli arg collision
        self.assertRaises(RuntimeError, GenericCLIAction, tool_id="TestCLI", input=[self.a1], additionalArgs={'input':None},
                          session=self.session)
        # illegal cli arg
        self.assertRaises(RuntimeError, GenericCLIAction ,tool_id="TestCLI", input=[self.a1], additionalArgs={'a':None},
                          illegalArgs=['a'],session=self.session)
        #invalid inputs
        self.assertRaises(RuntimeError, GenericCLIAction, tool_id="TestCLI", input=[self.a1], illegalArgs=['input'],
                          session=self.session)
        #illegal inputs output arg collision
        self.assertRaises(RuntimeError, GenericCLIAction, tool_id="TestCLI", input=[self.a1], outputFlags=['input'],
                          session=self.session)
        # illegal output arg
        self.assertRaises(RuntimeError, GenericCLIAction, tool_id="TestCLI", input=[self.a1], outputFlags=['illegal'],
                          illegalArgs=['illegal'], session=self.session)
        #invalid outputRefernceArtefactName
        self.assertRaises(ValueError, GenericCLIAction, tool_id="TestCLI", input=[self.a1],
                          outputReferenceArtefactName='invalidInput', session=self.session)


if __name__ == "__main__":
    unittest.main()