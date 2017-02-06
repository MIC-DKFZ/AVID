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
import avid.common.artefact.generator as artefactGenerator
from avid.actions.dummy import DummySingleAction as DummyAction
import avid.common.workflow as workflow
from avid.actions.threadingScheduler import ThreadingScheduler 

class TestThreadingScheduler(unittest.TestCase):
  def setUp(self):
    self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary","test_actions")
    self.testDataDir = os.path.join(os.path.split(__file__)[0],"data")
       
    self.session = workflow.Session("session1", self.sessionDir)
            
    self.a1 = artefactGenerator.generateArtefactEntry("Case1", None, 0, "Action1", "result", "dummy", os.path.join(self.testDataDir, "artefact1.txt"))
    self.a2 = artefactGenerator.generateArtefactEntry("Case1", None, 1, "Action2", "result", "dummy", os.path.join(self.testDataDir, "artefact1.txt"))
    self.a3 = artefactGenerator.generateArtefactEntry("Case1", None, 2, "Action3", "result", "dummy", os.path.join(self.testDataDir, "artefact1.txt"))
    self.a4 = artefactGenerator.generateArtefactEntry("Case2", None, 3, "Action4", "result", "dummy", os.path.join(self.testDataDir, "artefact1.txt"))
    self.a5 = artefactGenerator.generateArtefactEntry("Case2", None, 4, "Action5", "result", "dummy", os.path.join(self.testDataDir, "artefact1.txt"))
    self.a6 = artefactGenerator.generateArtefactEntry("Case2", None, 5, "Action6", "result", "dummy", os.path.join(self.testDataDir, "artefact1.txt"))

    self.session = workflow.Session("session1", self.sessionDir)
    workflow.currentGeneratedSession =self.session
    
    self.action1 = DummyAction([self.a1],"Action1", True)                
    self.action2 = DummyAction([self.a2],"Action2", True)                
    self.action3 = DummyAction([self.a3],"Action3", True)                
    self.action4 = DummyAction([self.a4],"Action4", True)                
    self.action5 = DummyAction([self.a5],"Action5", True)                
    self.action6 = DummyAction([self.a6],"Action6", True)
    
    self.actionList = [self.action1, self.action2, self.action3, self.action4, self.action5, self.action6]                


  def test_Scheduler(self):
    
    scheduler = ThreadingScheduler(3)
    
    tokens = scheduler.execute(self.actionList)
    
    self.assertIn(self.a1, self.session.artefacts)
    self.assertIn(self.a2, self.session.artefacts)
    self.assertIn(self.a3, self.session.artefacts)
    self.assertIn(self.a4, self.session.artefacts)
    self.assertIn(self.a5, self.session.artefacts)
    self.assertIn(self.a6, self.session.artefacts)
    
    self.assertEqual(len(tokens), 6)
    self.assertFalse(self.session.hasFailedActions())

if __name__ == '__main__':
    unittest.main()