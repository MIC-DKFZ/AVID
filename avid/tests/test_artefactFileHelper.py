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
import avid.common.artefact.fileHelper as fileHelper
import avid.common.artefact.generator as artefactGenerator
import avid.common.artefact as artefact
import avid.common.artefact.defaultProps as artefactProps

class TestArtefactFileHelper(unittest.TestCase):


    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data")
      self.rootTestDir = os.path.join(os.path.split(__file__)[0],"temporary")      
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary","test_artefactfilehelper")
              
      self.a1 = artefactGenerator.generateArtefactEntry("case1", None, 0, "action1", "result1", "dummy1", os.path.join(self.testDataDir, "artefact1.txt"), "obj_1", True)
      self.a2 = artefactGenerator.generateArtefactEntry("case2", None, 0, "action2", "result2", "dummy2", os.path.join(self.testDataDir, "artefact2.txt"), None, False, customProp1 = "nice", customProp2 = "42")
      self.data = list()
      self.data = artefact.addArtefactToWorkflowData(self.data, self.a1)
      self.data = artefact.addArtefactToWorkflowData(self.data, self.a2)


    def tearDown(self):
      try:
        shutil.rmtree(self.rootTestDir)
      except:
        pass


    def test_load_csv(self):
      
      with self.assertRaises(ValueError):
        fileHelper.loadArtefactList_csv("invalidFilePath")
      
      artefacts = fileHelper.loadArtefactList_csv(os.path.join(self.testDataDir,"artefactList.csv"),True)
      self.assertEqual(len(artefacts), 3)
      self.assertEqual(artefacts[0][artefactProps.CASE], "0")
      self.assertEqual(artefacts[0][artefactProps.TIMEPOINT], 0)
      self.assertEqual(artefacts[0][artefactProps.CASEINSTANCE], "")
      self.assertEqual(artefacts[0][artefactProps.TYPE], "result")
      self.assertEqual(artefacts[0][artefactProps.FORMAT], "virtuos")
      self.assertEqual(artefacts[0][artefactProps.URL], os.path.join(self.testDataDir, "artefact1.txt"))
      self.assertEqual(artefacts[0][artefactProps.ACTIONTAG], "Tag1")
      self.assertEqual(artefacts[0][artefactProps.OBJECTIVE], None)
      self.assertEqual(artefacts[0][artefactProps.INVALID], False)

      self.assertEqual(artefacts[1]["8"], "ownProp1")
      self.assertEqual(artefacts[1]["9"], "ownProp2")   
      
      #Check if auto check of url existance works properly: invalidation
      self.assertEqual(artefacts[2][artefactProps.CASE], "Case3")
      self.assertEqual(artefacts[2][artefactProps.INVALID], True)      

      artefacts = fileHelper.loadArtefactList_csv(os.path.join(self.testDataDir,"artefactList.csv"), rootPath = self.testDataDir)
      self.assertEqual(len(artefacts), 3)
      self.assertEqual(artefacts[0][artefactProps.CASE], "0")
      self.assertEqual(artefacts[0][artefactProps.TIMEPOINT], 0)
      self.assertEqual(artefacts[0][artefactProps.CASEINSTANCE], "")
      self.assertEqual(artefacts[0][artefactProps.TYPE], "result")
      self.assertEqual(artefacts[0][artefactProps.FORMAT], "virtuos")
      self.assertEqual(artefacts[0][artefactProps.URL], os.path.join(self.testDataDir, "artefact1.txt"))
      self.assertEqual(artefacts[0][artefactProps.ACTIONTAG], "Tag1")
      self.assertEqual(artefacts[0][artefactProps.OBJECTIVE], None)
      self.assertEqual(artefacts[0][artefactProps.INVALID], False)
      self.assertEqual(artefacts[1][artefactProps.INVALID], False)
      self.assertEqual(artefacts[2][artefactProps.INVALID], True)      

      artefacts = fileHelper.loadArtefactList_csv(os.path.join(self.testDataDir,"artefactList.csv"))
      self.assertEqual(len(artefacts), 3)
      self.assertEqual(artefacts[0][artefactProps.CASE], "0")
      self.assertEqual(artefacts[0][artefactProps.TIMEPOINT], 0)
      self.assertEqual(artefacts[0][artefactProps.CASEINSTANCE], "")
      self.assertEqual(artefacts[0][artefactProps.TYPE], "result")
      self.assertEqual(artefacts[0][artefactProps.FORMAT], "virtuos")
      self.assertEqual(artefacts[0][artefactProps.URL], "./artefact1.txt")
      self.assertEqual(artefacts[0][artefactProps.ACTIONTAG], "Tag1")
      self.assertEqual(artefacts[0][artefactProps.OBJECTIVE], None)
      self.assertEqual(artefacts[0][artefactProps.INVALID], True)
      self.assertEqual(artefacts[1][artefactProps.INVALID], True)
      self.assertEqual(artefacts[2][artefactProps.INVALID], True)      


    def test_load_xml(self):
      with self.assertRaises(ValueError):
        fileHelper.loadArtefactList_xml("invalidFilePath")
      
      artefacts = fileHelper.loadArtefactList_xml(os.path.join(self.testDataDir,"testlist.avid"),True)
      self.assertEqual(len(artefacts), 3)
      self.assertEqual(artefacts[0][artefactProps.ID], "ID_1")
      self.assertEqual(artefacts[0][artefactProps.CASE], "case_1")
      self.assertEqual(artefacts[0][artefactProps.TIMEPOINT], "time")
      self.assertEqual(artefacts[0][artefactProps.CASEINSTANCE], "instance_1")
      self.assertEqual(artefacts[0][artefactProps.TYPE], "type_1")
      self.assertEqual(artefacts[0][artefactProps.FORMAT], "format_1")
      self.assertEqual(artefacts[0][artefactProps.URL], os.path.join(self.testDataDir, "artefact1.txt"))
      self.assertEqual(artefacts[0][artefactProps.ACTIONTAG], "tag_1")
      self.assertEqual(artefacts[0][artefactProps.OBJECTIVE], "obj_1")
      self.assertEqual(artefacts[0][artefactProps.INVALID], False)

      self.assert_(artefacts[1][artefactProps.ID] is not None)
      self.assertEqual(artefacts[1][artefactProps.CASE], "case_2")
      self.assertEqual(artefacts[1][artefactProps.TIMEPOINT], 1)
      self.assertEqual(artefacts[1][artefactProps.CASEINSTANCE], None)
      self.assertEqual(artefacts[1][artefactProps.TYPE], None)
      self.assertEqual(artefacts[1][artefactProps.FORMAT], None)
      self.assertEqual(artefacts[1][artefactProps.URL], os.path.join(self.testDataDir,"invalid.file"))
      self.assertEqual(artefacts[1][artefactProps.ACTIONTAG], "UnkownAction")
      self.assertEqual(artefacts[1][artefactProps.OBJECTIVE], None)
      self.assertEqual(artefacts[1][artefactProps.INVALID], True)
      self.assertEqual(artefacts[1]["customProp"], "custom_1")
      
      #Check if auto check of url existance works properly: invalidation
      self.assertEqual(artefacts[2][artefactProps.CASE], "case_3")
      self.assertEqual(artefacts[2][artefactProps.TIMEPOINT], 2)
      self.assertEqual(artefacts[2][artefactProps.CASEINSTANCE], None)
      self.assertEqual(artefacts[2][artefactProps.TYPE], None)
      self.assertEqual(artefacts[2][artefactProps.FORMAT], None)
      self.assertEqual(artefacts[2][artefactProps.URL], os.path.join(self.testDataDir, "artefact2.txt"))
      self.assertEqual(artefacts[2][artefactProps.ACTIONTAG], "UnkownAction")
      self.assertEqual(artefacts[2][artefactProps.OBJECTIVE], None)
      self.assertEqual(artefacts[2][artefactProps.INVALID], True)      


    def test_save_xml(self):
      fileHelper.saveArtefactList_xml(os.path.join(self.sessionDir,"test1.avid"),self.data, rootPath = self.testDataDir)
      artefacts = fileHelper.loadArtefactList_xml(os.path.join(self.sessionDir,"test1.avid"), rootPath = self.testDataDir)
      
      self.assertListEqual(self.data, artefacts)


if __name__ == "__main__":
    unittest.main()