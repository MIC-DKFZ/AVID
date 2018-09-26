# AVID
# Automated workflow system for cohort analysis in radiology and radiation therapy
#
# Copyright (c) German Cancer Research Center,
# Software development for Integrated Diagnostic and Therapy (SIDT).
# All rights reserved.
#
# This software is distributed WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.
#
# See LICENSE.txt or http://www.dkfz.de/en/sidt/index.html for details.

import unittest
import os
import shutil
import avid.common.workflow as workflow
from avid.actions.pythonAction import PythonUnaryBatchAction as unaryPython
from avid.actions.pythonAction import PythonBinaryBatchAction as binaryPython
from avid.actions.pythonAction import PythonNaryBatchAction as naryPython
from avid.actions.pythonAction import PythonUnaryStackBatchAction as unaryStackPython
from avid.linkers import TimePointLinker

from avid.selectors.keyValueSelector import ActionTagSelector, ObjectiveSelector, TimepointSelector
from avid.common.artefact import defaultProps as artefactProps

def test_copy_script(inputs, outputs, times = 1):
    '''Simple python test script.'''
    with open(outputs[0], "w") as ofile:
        for input in inputs:
            with open(input, "r") as ifile:
                line = ifile.read()
                ofile.write(line*times)

def test_binary_copy_script(inputs1, inputs2, outputs, times = 1):
    '''Simple binary python test script.'''
    with open(outputs[0], "w") as ofile:
        for input in [inputs1[0],inputs2[0]]:
            with open(input, "r") as ifile:
                line = ifile.read()
                ofile.write(line*times)

def test_ternary_copy_script(inputsMaster, inputsSecond, inputsThird, outputs, times = 1):
    '''Simple ternary python test script.'''
    with open(outputs[0], "w") as ofile:
        with open(inputsMaster[0], "r") as ifile1:
            with open(inputsSecond[0], "r") as ifile2:
                with open(inputsThird[0], "r") as ifile3:
                    line1 = ifile1.read()
                    line2 = ifile2.read()
                    line3 = ifile3.read()
                    ofile.write(line1*times+'*'+line2*times+'+'+line3*times)

caseInstanceCount = 0
def indicate_nary_output_script(actionInstance, **allargs):
    global caseInstanceCount #used to ensure unique instances as result when testing
    caseInstanceCount += 1
    result = actionInstance.generateArtefact(actionInstance._inputArtefacts[sorted(actionInstance._inputArtefacts.keys())[0]],
                                             userDefinedProps={artefactProps.CASEINSTANCE: str(caseInstanceCount)},
                                             urlHumanPrefix=actionInstance.instanceName,
                                             urlExtension='txt')
    return [result]

def get_content(input):
    with open(input, "r") as ifile:
        line = ifile.read()
        return line

class TestPythonAction(unittest.TestCase):
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

    def test_unary_action(self):

      action = unaryPython(ActionTagSelector("stats"), generateCallable = test_copy_script,
                           passOnlyURLs = True, actionTag = "TestUnary")
      token = action.do()
                    
      self.assertEqual(token.isSuccess(), True)
      result = get_content(token.generatedArtefacts[0][artefactProps.URL])
      self.assertEqual(result, '1', True)
      result = get_content(token.generatedArtefacts[1][artefactProps.URL])
      self.assertEqual(result, '2', True)
      result = get_content(token.generatedArtefacts[2][artefactProps.URL])
      self.assertEqual(result, '3', True)

    def test_unary_action_with_user_argument(self):

        action = unaryPython(ActionTagSelector("stats"), generateCallable=test_copy_script, times = 3,
                             passOnlyURLs=True, actionTag="TestUnary")
        token = action.do()

        self.assertEqual(token.isSuccess(), True)
        result = get_content(token.generatedArtefacts[0][artefactProps.URL])
        self.assertEqual(result, '111', True)
        result = get_content(token.generatedArtefacts[1][artefactProps.URL])
        self.assertEqual(result, '222', True)
        result = get_content(token.generatedArtefacts[2][artefactProps.URL])
        self.assertEqual(result, '333', True)

    def test_binary_action(self):
        action = binaryPython(inputs1Selector = ObjectiveSelector("a"), inputs2Selector = ObjectiveSelector("b"), generateCallable=test_binary_copy_script,
                              indicateCallable=indicate_nary_output_script, passOnlyURLs=True, actionTag="TestBinary")
        token = action.do()

        self.assertEqual(token.isSuccess(), True)
        result = get_content(token.generatedArtefacts[0][artefactProps.URL])
        self.assertEqual(result, '12', True)
        result = get_content(token.generatedArtefacts[1][artefactProps.URL])
        self.assertEqual(result, '13', True)


    def test_binary_action_with_linker(self):
        action = binaryPython(inputs1Selector = ObjectiveSelector("a"), inputs2Selector = ObjectiveSelector("b"),
                              inputLinker=TimePointLinker(), generateCallable=test_binary_copy_script,
                              indicateCallable=indicate_nary_output_script, passOnlyURLs=True, actionTag="TestBinary")
        token = action.do()

        self.assertEqual(token.isSuccess(), True)
        result = get_content(token.generatedArtefacts[0][artefactProps.URL])
        self.assertEqual(result, '12', True)
        self.assertEqual(len(token.generatedArtefacts), 1)

    def test_binary_action_with_user_argument(self):
        action = binaryPython(inputs1Selector = ObjectiveSelector("a"), inputs2Selector = ObjectiveSelector("b"),
                              generateCallable=test_binary_copy_script, indicateCallable=indicate_nary_output_script,
                             passOnlyURLs=True, actionTag="TestBinary", times=3)
        token = action.do()

        self.assertEqual(token.isSuccess(), True)
        result = get_content(token.generatedArtefacts[0][artefactProps.URL])
        self.assertEqual(result, '111222', True)
        result = get_content(token.generatedArtefacts[1][artefactProps.URL])
        self.assertEqual(result, '111333', True)

    def test_nary_action(self):
        action = naryPython(inputsMaster = ObjectiveSelector('a'), inputsSecond = ObjectiveSelector('b'),
                            inputsThird = TimepointSelector(0),
                            generateCallable=test_ternary_copy_script, indicateCallable=indicate_nary_output_script,
                            passOnlyURLs=True, actionTag="TestNary")
        token = action.do()

        self.assertEqual(token.isSuccess(), True)
        result = get_content(token.generatedArtefacts[0][artefactProps.URL])
        self.assertEqual(result, '1*2+1', True)
        result = get_content(token.generatedArtefacts[1][artefactProps.URL])
        self.assertEqual(result, '1*2+2', True)
        result = get_content(token.generatedArtefacts[2][artefactProps.URL])
        self.assertEqual(result, '1*3+1', True)
        result = get_content(token.generatedArtefacts[3][artefactProps.URL])
        self.assertEqual(result, '1*3+2', True)
        self.assertEqual(len(token.generatedArtefacts), 4)

    def test_nary_action_with_linker(self):
        action = naryPython(inputsMaster = ObjectiveSelector('a'), inputsSecond = ObjectiveSelector('b'),
                            inputsThird = TimepointSelector(0), inputsSecondLinker=TimePointLinker(),
                            generateCallable=test_ternary_copy_script, indicateCallable=indicate_nary_output_script,
                            passOnlyURLs=True, actionTag="TestNary")
        token = action.do()

        self.assertEqual(token.isSuccess(), True)
        result = get_content(token.generatedArtefacts[0][artefactProps.URL])
        self.assertEqual(result, '1*2+1', True)
        result = get_content(token.generatedArtefacts[1][artefactProps.URL])
        self.assertEqual(result, '1*2+2', True)
        self.assertEqual(len(token.generatedArtefacts), 2)

    def test_unary_stack_action(self):
        action = unaryStackPython(ActionTagSelector("stats"), generateCallable=test_copy_script,
                             passOnlyURLs=True, actionTag="TestUnary")
        token = action.do()

        result = get_content(token.generatedArtefacts[0][artefactProps.URL])
        self.assertEqual(token.isSuccess(), True)
        self.assertEqual(result, '123', True)


    def test_unary_stack_action_with_user_argument(self):
        action = unaryStackPython(ActionTagSelector("stats"), generateCallable=test_copy_script, times = 3,
                             passOnlyURLs=True, actionTag="TestUnary")
        token = action.do()

        result = get_content(token.generatedArtefacts[0][artefactProps.URL])
        self.assertEqual(token.isSuccess(), True)
        self.assertEqual(result, '111222333', True)


    def test_unary_stack_split_action(self):
        action = unaryStackPython(ActionTagSelector("stats"), splitProperties = [artefactProps.OBJECTIVE],
                            generateCallable=test_copy_script, passOnlyURLs=True, actionTag="TestUnary")
        token = action.do()

        self.assertEqual(token.isSuccess(), True)
        result = get_content(token.generatedArtefacts[0][artefactProps.URL])
        self.assertEqual(result, '1', True)
        result = get_content(token.generatedArtefacts[1][artefactProps.URL])
        self.assertEqual(result, '23', True)

if __name__ == "__main__":
    unittest.main()