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
import asyncio
import threading
import time
import unittest
import os
import shutil
import avid.common.artefact.fileHelper as fileHelper
import avid.common.artefact.generator as artefactGenerator
import avid.common.artefact as artefact
import avid.common.artefact.defaultProps as artefactProps

def remove_lock_file(filepath):
  time.sleep(1)
  os.remove(filepath)

class TestArtefactFileHelper(unittest.TestCase):
    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data")
      self.rootTestDir = os.path.join(os.path.split(__file__)[0],"temporary")      
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary","test_artefactfilehelper")
              
      self.a1 = artefactGenerator.generateArtefactEntry("case1", None, 0, "action1", "result1", "dummy1", os.path.join(self.testDataDir, "artefact1.txt"), "obj_1", True)
      self.a2 = artefactGenerator.generateArtefactEntry("case2", None, 0, "action2", "result2", "dummy2", os.path.join(self.testDataDir, "artefact2.txt"), None, False, customProp1 = "nice", customProp2 = "42")
      self.a3 = artefactGenerator.generateArtefactEntry("case3", None, 0, "action1", "result1", "dummy1", os.path.join(self.testDataDir, "artefact1.txt"), input_ids = {'source':['id_1','id_1_1'], 'source3': [None], 'source4':['id_2']} )
      self.data = list()
      self.data = artefact.addArtefactToWorkflowData(self.data, self.a1)
      self.data = artefact.addArtefactToWorkflowData(self.data, self.a2)
      self.data = artefact.addArtefactToWorkflowData(self.data, self.a3)

      self.a3_update = artefactGenerator.generateArtefactEntry("case3", None, 0, "action1", "result1", "dummy1", os.path.join(self.testDataDir, "artefact3.txt"), input_ids = {'source':['id_1','id_1_1'], 'source3': [None], 'source4':['id_2']} )
      self.a4 = artefactGenerator.generateArtefactEntry("case4", None, 0, "action1", "result1", "dummy1", os.path.join(self.testDataDir, "artefact2.txt"))
      self.data_simelar = [self.a2, self.a3_update, self.a4]


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
      self.assertEqual(artefacts[1][artefactProps.ACTIONTAG], "UnknownAction")
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
      self.assertEqual(artefacts[2][artefactProps.ACTIONTAG], "UnknownAction")
      self.assertEqual(artefacts[2][artefactProps.OBJECTIVE], None)
      self.assertEqual(artefacts[2][artefactProps.INVALID], True)      
      self.assertDictEqual(artefacts[2][artefactProps.INPUT_IDS], {"input1":["ID_1","ID_1_2"], "input2":['ID_2']})

    def test_save_xml(self):
      fileHelper.saveArtefactList_xml(os.path.join(self.sessionDir,"test1.avid"),self.data, rootPath = self.testDataDir)
      artefacts = fileHelper.loadArtefactList_xml(os.path.join(self.sessionDir,"test1.avid"), rootPath = self.testDataDir)
      self.assertListEqual(self.data, artefacts)

    def test_update_artefactlist_simple(self):
      testFilePath = os.path.join(self.sessionDir,"test1.avid")
      fileHelper.saveArtefactList_xml(testFilePath,self.data, rootPath = self.testDataDir)

      fileHelper.update_artefactlist(testFilePath, self.data_simelar, rootPath = self.testDataDir)

      artefacts = fileHelper.loadArtefactList_xml(os.path.join(self.sessionDir,"test1.avid"), rootPath = self.testDataDir)
      referenceArtefacts = [self.a1, self.a2, self.a3, self.a4]
      self.assertListEqual(referenceArtefacts, artefacts)

      fileHelper.saveArtefactList_xml(testFilePath,self.data, savePathsRelative=False)

      fileHelper.update_artefactlist(testFilePath, self.data_simelar, savePathsRelative=False)

      artefacts = fileHelper.loadArtefactList_xml(os.path.join(self.sessionDir,"test1.avid"))
      referenceArtefacts = [self.a1, self.a2, self.a3, self.a4]
      self.assertListEqual(referenceArtefacts, artefacts)


    def test_update_artefactlist_update_existing(self):
      testFilePath = os.path.join(self.sessionDir,"test1.avid")
      fileHelper.saveArtefactList_xml(testFilePath,self.data, rootPath = self.testDataDir)

      fileHelper.update_artefactlist(testFilePath, self.data_simelar, update_existing=True, rootPath = self.testDataDir)

      artefacts = fileHelper.loadArtefactList_xml(os.path.join(self.sessionDir,"test1.avid"), rootPath = self.testDataDir)
      referenceArtefacts = [self.a1, self.a2, self.a3_update, self.a4]
      self.assertListEqual(referenceArtefacts, artefacts)

      fileHelper.saveArtefactList_xml(testFilePath,self.data, savePathsRelative=False)

      fileHelper.update_artefactlist(testFilePath, self.data_simelar, update_existing=True, savePathsRelative=False)

      artefacts = fileHelper.loadArtefactList_xml(os.path.join(self.sessionDir,"test1.avid"))
      referenceArtefacts = [self.a1, self.a2, self.a3_update, self.a4]
      self.assertListEqual(referenceArtefacts, artefacts)

    def test_update_artefactlist_waitfail(self):
      testFilePath = os.path.join(self.sessionDir,"test1.avid")
      fileHelper.saveArtefactList_xml(testFilePath,self.data, rootPath = self.testDataDir)

      lf_path = testFilePath+ os.extsep + 'update_lock'
      with open(lf_path, 'x') as lf:
        lf.write('dummy lock')

      access_denied = False
      try:
        fileHelper.update_artefactlist(testFilePath, self.data_simelar, rootPath = self.testDataDir, wait_time=1)
      except PermissionError:
        access_denied = True

      self.assertTrue(access_denied)


    def test_update_artefactlist_waitsuccess(self):

      testFilePath = os.path.join(self.sessionDir,"test1.avid")
      fileHelper.saveArtefactList_xml(testFilePath,self.data, rootPath = self.testDataDir)

      lf_path = testFilePath+ os.extsep + 'update_lock'
      with open(lf_path, 'x') as lf:
        lf.write('dummy lock')

      #trigger the process that will remove the lock in 2 sec to check if update_artefactlist will then work properly
      t = threading.Thread(target=remove_lock_file, args=(lf_path,))
      t.start()

      fileHelper.update_artefactlist(testFilePath, self.data_simelar, rootPath = self.testDataDir)
      t.join()


if __name__ == "__main__":
    unittest.main()