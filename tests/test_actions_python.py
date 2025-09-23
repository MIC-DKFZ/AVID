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
from avid.actions.pythonAction import PythonBinaryBatchAction as binaryPython
from avid.actions.pythonAction import PythonNaryBatchAction as naryPython
from avid.actions.pythonAction import PythonNaryBatchActionV2 as naryPythonV2
from avid.actions.pythonAction import PythonUnaryBatchAction as unaryPython
from avid.actions.pythonAction import PythonUnaryStackBatchAction as unaryStackPython
from avid.common.artefact import defaultProps as artefactProps
from avid.linkers import TimePointLinker
from avid.selectors.keyValueSelector import (
    ActionTagSelector,
    ObjectiveSelector,
    TimepointSelector,
)


def test_copy_script(inputs, outputs, times=1):
    """Simple python test script."""
    with open(outputs[0], "w") as ofile:
        for input in inputs:
            with open(input, "r") as ifile:
                line = ifile.read()
                ofile.write(line * times)


def test_binary_copy_script(inputs1, inputs2, outputs, times=1):
    """Simple binary python test script."""
    with open(outputs[0], "w") as ofile:
        for input in [inputs1[0], inputs2[0]]:
            with open(input, "r") as ifile:
                line = ifile.read()
                ofile.write(line * times)


def test_ternary_copy_script(inputsMaster, inputsSecond, inputsThird, outputs, times=1):
    """Simple ternary python test script."""
    with open(outputs[0], "w") as ofile:
        with open(inputsMaster[0], "r") as ifile1:
            with open(inputsSecond[0], "r") as ifile2:
                with open(inputsThird[0], "r") as ifile3:
                    line1 = ifile1.read()
                    line2 = ifile2.read()
                    line3 = ifile3.read()
                    ofile.write(
                        line1 * times + "*" + line2 * times + "+" + line3 * times
                    )


def test_nary_v2_copy_script(aInput, bInput, cInput, outputs, times=1):
    """Simple ternary python test script."""
    with open(outputs[0], "w") as ofile:
        with open(aInput[0], "r") as ifile1:
            with open(bInput[0], "r") as ifile2:
                with open(cInput[0], "r") as ifile3:
                    line1 = ifile1.read()
                    line2 = ifile2.read()
                    line3 = ifile3.read()
                    ofile.write(
                        line1 * times + "*" + line2 * times + "+" + line3 * times
                    )


caseInstanceCount = 0


def indicate_nary_output_script(actionInstance, **allargs):
    global caseInstanceCount  # used to ensure unique instances as result when testing
    caseInstanceCount += 1
    result = actionInstance.generateArtefact(
        actionInstance._inputArtefacts[
            sorted(actionInstance._inputArtefacts.keys())[0]
        ][0],
        userDefinedProps={artefactProps.CASEINSTANCE: str(caseInstanceCount)},
        url_user_defined_part=actionInstance.instanceName,
        url_extension="txt",
    )
    return [result]


def get_content(input):
    with open(input, "r") as ifile:
        line = ifile.read()
        return line


class TestPythonAction(unittest.TestCase):
    def setUp(self):
        self.testDataDir = os.path.join(
            os.path.split(__file__)[0], "data", "pythonActionTest"
        )
        self.testArtefactFile = os.path.join(
            os.path.split(__file__)[0], "data", "pythonActionTest", "testlist.avid"
        )
        self.sessionDir = os.path.join(
            os.path.split(__file__)[0], "temporary_test_pythonAction"
        )

        self.session = workflow.initSession(
            os.path.join(self.sessionDir, "test.avid"),
            expandPaths=True,
            bootstrapArtefacts=self.testArtefactFile,
        )

    def tearDown(self):
        try:
            shutil.rmtree(self.sessionDir)
        except:
            pass

    def test_unary_action(self):

        action = unaryPython(
            ActionTagSelector("stats"),
            generateCallable=test_copy_script,
            passOnlyURLs=True,
            actionTag="TestUnary",
        )
        action.do()

        self.assertEqual(action.isSuccess, True)
        result = get_content(action.outputArtefacts[0][artefactProps.URL])
        self.assertEqual(result, "1")
        result = get_content(action.outputArtefacts[1][artefactProps.URL])
        self.assertEqual(result, "2")
        result = get_content(action.outputArtefacts[2][artefactProps.URL])
        self.assertEqual(result, "3")

    def test_unary_action_with_user_argument(self):

        action = unaryPython(
            ActionTagSelector("stats"),
            generateCallable=test_copy_script,
            additionalArgs={"times": 3},
            passOnlyURLs=True,
            actionTag="TestUnary",
        )
        action.do()

        self.assertEqual(action.isSuccess, True)
        result = get_content(action.outputArtefacts[0][artefactProps.URL])
        self.assertEqual(result, "111")
        result = get_content(action.outputArtefacts[1][artefactProps.URL])
        self.assertEqual(result, "222")
        result = get_content(action.outputArtefacts[2][artefactProps.URL])
        self.assertEqual(result, "333")

    def test_binary_action(self):
        action = binaryPython(
            inputs1Selector=ObjectiveSelector("a"),
            inputs2Selector=ObjectiveSelector("b"),
            generateCallable=test_binary_copy_script,
            indicateCallable=indicate_nary_output_script,
            passOnlyURLs=True,
            actionTag="TestBinary",
        )
        action.do()

        self.assertEqual(action.isSuccess, True)
        result = get_content(action.outputArtefacts[0][artefactProps.URL])
        self.assertEqual(result, "12")
        result = get_content(action.outputArtefacts[1][artefactProps.URL])
        self.assertEqual(result, "13")

    def test_binary_action_with_linker(self):
        action = binaryPython(
            inputs1Selector=ObjectiveSelector("a"),
            inputs2Selector=ObjectiveSelector("b"),
            inputLinker=TimePointLinker(),
            generateCallable=test_binary_copy_script,
            indicateCallable=indicate_nary_output_script,
            passOnlyURLs=True,
            actionTag="TestBinary",
        )
        action.do()

        self.assertEqual(action.isSuccess, True)
        result = get_content(action.outputArtefacts[0][artefactProps.URL])
        self.assertEqual(result, "12")
        self.assertEqual(len(action.outputArtefacts), 1)

    def test_binary_action_with_user_argument(self):
        action = binaryPython(
            inputs1Selector=ObjectiveSelector("a"),
            inputs2Selector=ObjectiveSelector("b"),
            generateCallable=test_binary_copy_script,
            indicateCallable=indicate_nary_output_script,
            passOnlyURLs=True,
            actionTag="TestBinary",
            additionalArgs={"times": 3},
        )
        action.do()

        self.assertEqual(action.isSuccess, True)
        result = get_content(action.outputArtefacts[0][artefactProps.URL])
        self.assertEqual(result, "111222")
        result = get_content(action.outputArtefacts[1][artefactProps.URL])
        self.assertEqual(result, "111333")

    def test_nary_action(self):
        action = naryPython(
            inputsMaster=ObjectiveSelector("a"),
            inputsSecond=ObjectiveSelector("b"),
            inputsThird=TimepointSelector(0),
            generateCallable=test_ternary_copy_script,
            indicateCallable=indicate_nary_output_script,
            passOnlyURLs=True,
            actionTag="TestNary",
        )
        action.do()

        self.assertEqual(action.isSuccess, True)
        result = get_content(action.outputArtefacts[0][artefactProps.URL])
        self.assertEqual(result, "1*2+1")
        result = get_content(action.outputArtefacts[1][artefactProps.URL])
        self.assertEqual(result, "1*2+2")
        result = get_content(action.outputArtefacts[2][artefactProps.URL])
        self.assertEqual(result, "1*3+1")
        result = get_content(action.outputArtefacts[3][artefactProps.URL])
        self.assertEqual(result, "1*3+2")
        self.assertEqual(len(action.outputArtefacts), 4)

    def test_nary_action_with_linker(self):
        action = naryPython(
            inputsMaster=ObjectiveSelector("a"),
            inputsSecond=ObjectiveSelector("b"),
            inputsThird=TimepointSelector(0),
            inputsSecondLinker=TimePointLinker(),
            generateCallable=test_ternary_copy_script,
            indicateCallable=indicate_nary_output_script,
            passOnlyURLs=True,
            actionTag="TestNary",
        )
        action.do()

        self.assertEqual(action.isSuccess, True)
        result = get_content(action.outputArtefacts[0][artefactProps.URL])
        self.assertEqual(result, "1*2+1")
        result = get_content(action.outputArtefacts[1][artefactProps.URL])
        self.assertEqual(result, "1*2+2")
        self.assertEqual(len(action.outputArtefacts), 2)

    def test_unary_stack_action(self):
        action = unaryStackPython(
            ActionTagSelector("stats"),
            generateCallable=test_copy_script,
            passOnlyURLs=True,
            actionTag="TestUnary",
        )
        action.do()

        result = get_content(action.outputArtefacts[0][artefactProps.URL])
        self.assertEqual(action.isSuccess, True)
        self.assertEqual(result, "123")

    def test_unary_stack_action_with_user_argument(self):
        action = unaryStackPython(
            ActionTagSelector("stats"),
            generateCallable=test_copy_script,
            additionalArgs={"times": 3},
            passOnlyURLs=True,
            actionTag="TestUnary",
        )
        action.do()

        result = get_content(action.outputArtefacts[0][artefactProps.URL])
        self.assertEqual(action.isSuccess, True)
        self.assertEqual(result, "111222333")

    def test_unary_stack_split_action(self):
        action = unaryStackPython(
            ActionTagSelector("stats"),
            splitProperties=[artefactProps.OBJECTIVE],
            generateCallable=test_copy_script,
            passOnlyURLs=True,
            actionTag="TestUnarySplit",
        )
        action.do()

        self.assertEqual(action.isSuccess, True)
        result = get_content(action.outputArtefacts[0][artefactProps.URL])
        self.assertEqual(result, "1")
        result = get_content(action.outputArtefacts[1][artefactProps.URL])
        self.assertEqual(result, "23")

    def test_nary_v2_action(self):
        action = naryPythonV2(
            primaryInputSelector=ObjectiveSelector("a"),
            primaryAlias="aInput",
            additionalInputSelectors={
                "bInput": ObjectiveSelector("b"),
                "cInput": TimepointSelector(0),
            },
            generateCallable=test_nary_v2_copy_script,
            indicateCallable=indicate_nary_output_script,
            passOnlyURLs=True,
            actionTag="TestNaryV2",
        )
        action.do()

        self.assertEqual(action.isSuccess, True)
        result = get_content(action.outputArtefacts[0][artefactProps.URL])
        self.assertEqual(result, "1*2+1")
        result = get_content(action.outputArtefacts[1][artefactProps.URL])
        self.assertEqual(result, "1*2+2")
        result = get_content(action.outputArtefacts[2][artefactProps.URL])
        self.assertEqual(result, "1*3+1")
        result = get_content(action.outputArtefacts[3][artefactProps.URL])
        self.assertEqual(result, "1*3+2")
        self.assertEqual(len(action.outputArtefacts), 4)

    def test_nary_v2_action_with_user_argument(self):
        action = naryPythonV2(
            primaryInputSelector=ObjectiveSelector("a"),
            primaryAlias="aInput",
            additionalInputSelectors={
                "bInput": ObjectiveSelector("b"),
                "cInput": TimepointSelector(0),
            },
            additionalArgs={"times": 4},
            generateCallable=test_nary_v2_copy_script,
            indicateCallable=indicate_nary_output_script,
            passOnlyURLs=True,
            actionTag="TestNaryV2_times",
        )
        action.do()

        self.assertEqual(action.isSuccess, True)
        result = get_content(action.outputArtefacts[0][artefactProps.URL])
        self.assertEqual(result, "1111*2222+1111")
        result = get_content(action.outputArtefacts[1][artefactProps.URL])
        self.assertEqual(result, "1111*2222+2222")
        result = get_content(action.outputArtefacts[2][artefactProps.URL])
        self.assertEqual(result, "1111*3333+1111")
        result = get_content(action.outputArtefacts[3][artefactProps.URL])
        self.assertEqual(result, "1111*3333+2222")
        self.assertEqual(len(action.outputArtefacts), 4)

    def test_nary_v2_action_with_user_argument_and_linker(self):
        action = naryPythonV2(
            primaryInputSelector=ObjectiveSelector("a"),
            primaryAlias="aInput",
            additionalInputSelectors={
                "bInput": ObjectiveSelector("b"),
                "cInput": TimepointSelector(0),
            },
            linker={"bInput": TimePointLinker()},
            additionalArgs={"times": 4},
            generateCallable=test_nary_v2_copy_script,
            indicateCallable=indicate_nary_output_script,
            passOnlyURLs=True,
            actionTag="TestNaryV2_times_linker",
        )
        action.do()

        self.assertEqual(action.isSuccess, True)
        result = get_content(action.outputArtefacts[0][artefactProps.URL])
        self.assertEqual(result, "1111*2222+1111")
        result = get_content(action.outputArtefacts[1][artefactProps.URL])
        self.assertEqual(result, "1111*2222+2222")
        self.assertEqual(len(action.outputArtefacts), 2)

    def test_nary_action_with_linker(self):
        action = naryPython(
            inputsMaster=ObjectiveSelector("a"),
            inputsSecond=ObjectiveSelector("b"),
            inputsThird=TimepointSelector(0),
            inputsSecondLinker=TimePointLinker(),
            generateCallable=test_ternary_copy_script,
            indicateCallable=indicate_nary_output_script,
            passOnlyURLs=True,
            actionTag="TestNary",
        )
        action.do()

        self.assertEqual(action.isSuccess, True)
        result = get_content(action.outputArtefacts[0][artefactProps.URL])
        self.assertEqual(result, "1*2+1")
        result = get_content(action.outputArtefacts[1][artefactProps.URL])
        self.assertEqual(result, "1*2+2")
        self.assertEqual(len(action.outputArtefacts), 2)


if __name__ == "__main__":
    unittest.main()
