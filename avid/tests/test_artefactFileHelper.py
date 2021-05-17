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
      self.a3 = artefactGenerator.generateArtefactEntry("case3", None, 0, "action1", "result1", "dummy1", os.path.join(self.testDataDir, "artefact1.txt"), input_ids = {'source':['id_1','id_1_1'], 'source2':None, 'source3': [None], 'source4':['id_2']} )
      self.data = list()
      self.data = artefact.addArtefactToWorkflowData(self.data, self.a1)
      self.data = artefact.addArtefactToWorkflowData(self.data, self.a2)
      self.data = artefact.addArtefactToWorkflowData(self.data, self.a3)

      self.a3_loaded = artefactGenerator.generateArtefactEntry("case3", None, 0, "action1", "result1", "dummy1", os.path.join(self.testDataDir, "artefact1.txt"), input_ids = {'source':['id_1','id_1_1'], 'source4':['id_2']} )
      self.a3_loaded[artefactProps.ID] = self.a3[artefactProps.ID]
      self.data_loaded = list()
      self.data_loaded = artefact.addArtefactToWorkflowData(self.data_loaded, self.a1)
      self.data_loaded = artefact.addArtefactToWorkflowData(self.data_loaded, self.a2)
      self.data_loaded = artefact.addArtefactToWorkflowData(self.data_loaded, self.a3_loaded)


    def tearDown(self):
      try:
        shutil.rmtree(self.rootTestDir)
      except:
        pass

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
      self.assertEqual(artefacts[0][artefactProps.INPUT_IDS], None)

      self.assertTrue(artefacts[1][artefactProps.ID] is not None)
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
      self.assertEqual(artefacts[1][artefactProps.INPUT_IDS], None)
      
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
      self.assertDictEqual(artefacts[2][artefactProps.INPUT_IDS], {"input1":["ID_1","ID_1_2"], "input2":['ID_2']})


    def test_save_xml(self):

      fileHelper.saveArtefactList_xml(os.path.join(self.sessionDir,"test1.avid"),self.data, rootPath = self.testDataDir)
      artefacts = fileHelper.loadArtefactList_xml(os.path.join(self.sessionDir,"test1.avid"), rootPath = self.testDataDir)
      self.assertListEqual(self.data_loaded, artefacts)


if __name__ == "__main__":
    unittest.main()