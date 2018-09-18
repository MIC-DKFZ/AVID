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
from avid.actions.pythonAction import PythonNaryBatchAction as naryPython

from avid.selectors.keyValueSelector import ActionTagSelector
from avid.common.artefact import defaultProps as artefactProps

def test_copy_script(inputs, outputs, times = 1):
    '''Simple python test script.'''
    with open(outputs[0], "w") as ofile:
        for input in inputs:
            with open(input, "r") as ifile:
                line = ifile.read()
                ofile.write(line*times)

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

    def test_nary_action(self):
        action = naryPython(ActionTagSelector("stats"), generateCallable=test_copy_script,
                             passOnlyURLs=True, actionTag="TestUnary")
        token = action.do()

        result = get_content(token.generatedArtefacts[0][artefactProps.URL])
        self.assertEqual(token.isSuccess(), True)
        self.assertEqual(result, '123', True)


    def test_nary_action_with_user_argument(self):
        action = naryPython(ActionTagSelector("stats"), generateCallable=test_copy_script, times = 3,
                             passOnlyURLs=True, actionTag="TestUnary")
        token = action.do()

        result = get_content(token.generatedArtefacts[0][artefactProps.URL])
        self.assertEqual(token.isSuccess(), True)
        self.assertEqual(result, '111222333', True)


    def test_nary_split_action(self):
        action = naryPython(ActionTagSelector("stats"), splitProperties = [artefactProps.OBJECTIVE],
                            generateCallable=test_copy_script, passOnlyURLs=True, actionTag="TestUnary")
        token = action.do()

        self.assertEqual(token.isSuccess(), True)
        result = get_content(token.generatedArtefacts[0][artefactProps.URL])
        self.assertEqual(result, '1', True)
        result = get_content(token.generatedArtefacts[1][artefactProps.URL])
        self.assertEqual(result, '23', True)

if __name__ == "__main__":
    unittest.main()