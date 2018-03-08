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
import shutil
import unittest
import avid.common.workflow as workflow
import os
from avid.actions.dummy import DummyBatchAction
from avid.actions import BatchActionBase
import avid.common.artefact.generator as artefactGenerator
import avid.common.artefact as artefact
import avid.common.artefact.defaultProps as artefactProps
from avid.selectors.keyValueSelector import CaseSelector

class Test(unittest.TestCase):

    def setUp(self):
        self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_actions")
        self.testDataDir = os.path.join(os.path.split(__file__)[0],"data")

        self.a_valid = artefactGenerator.generateArtefactEntry("Case1", 0, 0, "Action1", artefactProps.TYPE_VALUE_RESULT, "dummy", os.path.join(self.testDataDir, "artefact1.txt"))
        self.a_valid2 = artefactGenerator.generateArtefactEntry("Case2", 2, 0, "Action3", artefactProps.TYPE_VALUE_RESULT, "dummy", os.path.join(self.testDataDir, "artefact2.txt"))
        self.a_NoneURL = artefactGenerator.generateArtefactEntry("Case2", 1, 0, "Action1", artefactProps.TYPE_VALUE_RESULT, "dummy", None)
        self.a_NoFile = artefactGenerator.generateArtefactEntry("Case3", 1, 0, "Action1", artefactProps.TYPE_VALUE_RESULT, "dummy", "notexistingFile")
        self.a_Invalid = artefactGenerator.generateArtefactEntry("Case2", 2, 0, "Action1", artefactProps.TYPE_VALUE_RESULT, "dummy", os.path.join(self.testDataDir, "artefact2.txt"), None, True)
        
        self.a_valid_new = artefactGenerator.generateArtefactEntry("Case1", 0, 0, "Action1", artefactProps.TYPE_VALUE_RESULT, "dummy", os.path.join(self.testDataDir, "artefact1.txt"))
        self.a_valid2_new = artefactGenerator.generateArtefactEntry("Case2", 2, 0, "Action3", artefactProps.TYPE_VALUE_RESULT, "dummy", os.path.join(self.testDataDir, "artefact2.txt"))
        self.a_Invalid_new = artefactGenerator.generateArtefactEntry("Case2", 2, 0, "Action1", artefactProps.TYPE_VALUE_RESULT, "dummy", os.path.join(self.testDataDir, "artefact2.txt"))
 
        self.session = workflow.Session("session1", self.sessionDir)
        artefact.addArtefactToWorkflowData(self.session.artefacts,self.a_valid)
        artefact.addArtefactToWorkflowData(self.session.artefacts,self.a_valid2)
        artefact.addArtefactToWorkflowData(self.session.artefacts,self.a_NoneURL)
        artefact.addArtefactToWorkflowData(self.session.artefacts,self.a_NoFile)
        artefact.addArtefactToWorkflowData(self.session.artefacts,self.a_Invalid)
        

    def tearDown(self):
        try:
            shutil.rmtree(self.sessionDir)
        except:
            pass


    def testName(self):
        return "Test BatchActionBase"

        
    def test_simelar_exisiting_alwaysDo(self):
      workflow.currentGeneratedSession = self.session
      action = DummyBatchAction([self.a_valid_new, self.a_valid2_new],"Action1", True)
      
      token = action.do()
      
      self.assert_(token.isSuccess())
      self.assertIn(self.a_valid_new, token.generatedArtefacts)
      self.assertIn(self.a_valid2_new, token.generatedArtefacts)
      self.assertEqual(len(token.generatedArtefacts), 2)
      self.assertEqual(token.actionTag, action.actionTag)
      self.assertEqual(self.session.actions[action.actionTag], token)
      self.assertIn(self.a_valid_new, self.session.artefacts)
      self.assertIn(self.a_valid2_new, self.session.artefacts)
      

    def test_simelar_exisiting_alwaysOff(self):
      workflow.currentGeneratedSession = self.session
      action = DummyBatchAction([self.a_valid_new, self.a_valid2_new],"Action1", False)
      
      token = action.do()
      
      self.assert_(token.isSkipped())
      self.assertIn(self.a_valid, token.generatedArtefacts)
      self.assertIn(self.a_valid2, token.generatedArtefacts)
      self.assertEqual(len(token.generatedArtefacts), 2)
      self.assertEqual(token.actionTag, action.actionTag)
      self.assertEqual(self.session.actions[action.actionTag], token)
      self.assertIn(self.a_valid, self.session.artefacts)
      self.assertIn(self.a_valid2, self.session.artefacts)
      self.assertFalse(self.a_valid_new in self.session.artefacts)
      self.assertFalse(self.a_valid2_new in self.session.artefacts)


    def test_simelar_mixed_alwaysDo(self):
      workflow.currentGeneratedSession = self.session
      action = DummyBatchAction([self.a_valid_new, self.a_Invalid_new],"Action1", True)
      
      token = action.do()
      
      self.assert_(token.isSuccess())
      self.assertIn(self.a_valid_new, token.generatedArtefacts)
      self.assertIn(self.a_Invalid_new, token.generatedArtefacts)
      self.assertEqual(len(token.generatedArtefacts), 2)
      self.assertEqual(token.actionTag, action.actionTag)
      self.assertEqual(self.session.actions[action.actionTag], token)
      self.assertIn(self.a_valid_new, self.session.artefacts)
      self.assertIn(self.a_Invalid_new, self.session.artefacts)


    def test_simelar_mixed_alwaysOff(self):
      workflow.currentGeneratedSession = self.session
      action = DummyBatchAction([self.a_valid_new, self.a_Invalid_new],"Action1", False)
      
      token = action.do()
      
      self.assert_(token.isSuccess())
      self.assertIn(self.a_valid, token.generatedArtefacts)
      self.assertIn(self.a_Invalid_new, token.generatedArtefacts)
      self.assertEqual(len(token.generatedArtefacts), 2)
      self.assertEqual(token.actionTag, action.actionTag)
      self.assertEqual(self.session.actions[action.actionTag], token)
      self.assertIn(self.a_valid, self.session.artefacts)
      self.assertIn(self.a_Invalid_new, self.session.artefacts)
      self.assertFalse(self.a_valid_new in self.session.artefacts)
      self.assertFalse(self.a_Invalid in self.session.artefacts)


    def test_failure_mixed_alwaysOn(self):
      workflow.currentGeneratedSession = self.session
      action = DummyBatchAction([self.a_valid_new, self.a_NoFile],"Action1", True)
      
      token = action.do()
      
      self.assert_(token.isFailure())
      self.assertIn(self.a_valid_new, token.generatedArtefacts)
      self.assertIn(self.a_NoFile, token.generatedArtefacts)
      self.assertEqual(len(token.generatedArtefacts), 2)
      self.assertEqual(token.actionTag, action.actionTag)
      self.assertEqual(self.session.actions[action.actionTag], token)
      self.assertIn(self.a_valid_new, self.session.artefacts)
      self.assertIn(self.a_NoFile, self.session.artefacts)
      self.assert_(token.generatedArtefacts[1][artefactProps.INVALID])

    
    def test_failure_mixed_alwaysOff(self):
      workflow.currentGeneratedSession = self.session
      action = DummyBatchAction([self.a_valid_new, self.a_NoFile],"Action1")
      
      token = action.do()
      
      self.assertTrue(token.isFailure())
      self.assertIn(self.a_valid, token.generatedArtefacts)
      self.assertIn(self.a_NoFile, token.generatedArtefacts)
      self.assertEqual(len(token.generatedArtefacts), 2)
      self.assertEqual(token.actionTag, action.actionTag)
      self.assertEqual(self.session.actions[action.actionTag], token)
      self.assertIn(self.a_valid, self.session.artefacts)
      self.assertIn(self.a_NoFile, self.session.artefacts)
      self.assert_(token.generatedArtefacts[1][artefactProps.INVALID])


    def test_ensure_valid_artifacts_additional_selector(self):
      workflow.currentGeneratedSession = self.session
      action = BatchActionBase("Action1")
      
      selection = action.ensureRelevantArtefacts(self.session.artefacts, CaseSelector("Case2"))
     
      self.assertTrue(len(selection)==3)
      self.assertIn(self.a_valid2, selection)
      self.assertIn(self.a_NoneURL, selection)
      self.assertIn(self.a_Invalid, selection)
      

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()