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
import os
import shutil
import threading
import time
import unittest

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact.fileHelper as fileHelper
import avid.common.artefact.generator as artefactGenerator
from avid.common.artefact import ArtefactCollection


def remove_lock_file(filepath):
    time.sleep(1)
    os.remove(filepath)

def make_load_test_condition(ref_artefacts):
    def check(artefact):
        valid_artefact = False
        # check if the artefacts matches with one of the references
        for refA in ref_artefacts:
            ref_match = True
            for key in refA:
                if not refA[key] == artefact[key]:
                    ref_match = False
                    break
            if ref_match:
                valid_artefact = True
        return valid_artefact
    return check


class TestArtefactFileHelper(unittest.TestCase):
    def setUp(self):
        self.testDataDir = os.path.join(os.path.split(__file__)[0], "data")
        self.rootTestDir = os.path.join(os.path.split(__file__)[0], "temporary")
        self.sessionDir = os.path.join(os.path.split(__file__)[0], "temporary", "test_artefactfilehelper")

        self.a1 = artefactGenerator.generateArtefactEntry("case1", None, 0, "action1", "result1", "dummy1",
                                                          os.path.join(self.testDataDir, "artefact1.txt"), "obj_1",
                                                          True)
        self.a2 = artefactGenerator.generateArtefactEntry("case2", None, 0, "action2", "result2", "dummy2",
                                                          os.path.join(self.testDataDir, "artefact2.txt"), None, False,
                                                          customProp1="nice", customProp2="42")
        self.a3 = artefactGenerator.generateArtefactEntry("case3", None, 0, "action1", "result1", "dummy1",
                                                          os.path.join(self.testDataDir, "artefact1.txt"),
                                                          input_ids={'source': ['id_1', 'id_1_1'], 'source3': [None],
                                                                     'source4': ['id_2']})
        self.data = ArtefactCollection()
        self.data.add_artefact(self.a1)
        self.data.add_artefact(self.a2)
        self.data.add_artefact(self.a3)

        self.a3_update = artefactGenerator.generateArtefactEntry("case3", None, 0, "action1", "result1", "dummy1",
                                                                 os.path.join(self.testDataDir, "artefact3.txt"),
                                                                 input_ids={'source': ['id_1', 'id_1_1'],
                                                                            'source3': [None], 'source4': ['id_2']})
        self.a4 = artefactGenerator.generateArtefactEntry("case4", None, 0, "action1", "result1", "dummy1",
                                                          os.path.join(self.testDataDir, "artefact2.txt"))
        self.data_simelar = [self.a2, self.a3_update, self.a4]

    def tearDown(self):
        try:
            shutil.rmtree(self.rootTestDir)
        except:
            pass

    def test_load_xml(self):
        with self.assertRaises(ValueError):
            fileHelper.load_artefact_collection_from_xml("invalidFilePath")

        refA1 = dict()
        refA1[artefactProps.ID] = "ID_1"
        refA1[artefactProps.CASE] = "case_1"
        refA1[artefactProps.TIMEPOINT] = "time"
        refA1[artefactProps.CASEINSTANCE] = "instance_1"
        refA1[artefactProps.TYPE] = "type_1"
        refA1[artefactProps.FORMAT] = "format_1"
        refA1[artefactProps.URL] = os.path.join(self.testDataDir, "artefact1.txt")
        refA1[artefactProps.ACTIONTAG] = "tag_1"
        refA1[artefactProps.OBJECTIVE] = "obj_1"
        refA1[artefactProps.INVALID] = False
        refA1[artefactProps.INPUT_IDS] = None

        refA2 = dict()
        refA2[artefactProps.CASE] = "case_2"
        refA2[artefactProps.TIMEPOINT] = 1
        refA2[artefactProps.CASEINSTANCE] = None
        refA2[artefactProps.TYPE] = None
        refA2[artefactProps.FORMAT] = None
        refA2[artefactProps.URL] = os.path.join(self.testDataDir, "invalid.file")
        refA2[artefactProps.ACTIONTAG] = "UnknownAction"
        refA2[artefactProps.OBJECTIVE] = None
        refA2[artefactProps.INVALID] = True
        refA2["customProp"] = "custom_1"
        refA2[artefactProps.INPUT_IDS] = None

        # Check if auto check of url existance works properly: invalidation
        refA3 = dict()
        refA3[artefactProps.CASE] = "case_3"
        refA3[artefactProps.TIMEPOINT] = 2
        refA3[artefactProps.CASEINSTANCE] = None
        refA3[artefactProps.TYPE] = None
        refA3[artefactProps.FORMAT] = None
        refA3[artefactProps.URL] = os.path.join(self.testDataDir, "artefact2.txt")
        refA3[artefactProps.ACTIONTAG] = "UnknownAction"
        refA3[artefactProps.OBJECTIVE] = None
        refA3[artefactProps.INVALID] = True
        refA3[artefactProps.INPUT_IDS] = {"input1": ["ID_1", "ID_1_2"], "input2": ['ID_2']}

        ref_artefacts = [refA1, refA2, refA3]
        condition = make_load_test_condition(ref_artefacts)

        artefacts = fileHelper.load_artefact_collection_from_xml(os.path.join(self.testDataDir, "testlist.avid"), True)
        self.assertEqual(len(artefacts), 3)
        for artefact in artefacts:
            self.assertTrue(artefact[artefactProps.ID] is not None)
        valid_artefact = [x for x in artefacts if condition(x)]
        self.assertEqual(len(valid_artefact), 3)

    def test_save_xml(self):
        fileHelper.save_artefacts_to_xml(os.path.join(self.sessionDir, "test1.avid"), self.data,
                                         rootPath=self.testDataDir)
        artefacts = fileHelper.load_artefact_collection_from_xml(os.path.join(self.sessionDir, "test1.avid"),
                                                                 rootPath=self.testDataDir)
        self.assertEqual(self.data, artefacts)

    def test_update_artefactlist_simple(self):
        testFilePath = os.path.join(self.sessionDir, "test1.avid")
        fileHelper.save_artefacts_to_xml(testFilePath, self.data, rootPath=self.testDataDir)

        fileHelper.update_artefactlist(testFilePath, self.data_simelar, rootPath=self.testDataDir)

        artefacts = fileHelper.load_artefact_collection_from_xml(os.path.join(self.sessionDir, "test1.avid"),
                                                                 rootPath=self.testDataDir)
        referenceArtefacts = [self.a1, self.a2, self.a3, self.a4]
        self.assertTrue(artefacts.collection_is_similar(referenceArtefacts))

        fileHelper.save_artefacts_to_xml(testFilePath, self.data, savePathsRelative=False)

        fileHelper.update_artefactlist(testFilePath, self.data_simelar, savePathsRelative=False)

        artefacts = fileHelper.load_artefact_collection_from_xml(os.path.join(self.sessionDir, "test1.avid"))
        referenceArtefacts = [self.a1, self.a2, self.a3, self.a4]
        self.assertTrue(artefacts.collection_is_similar(referenceArtefacts))

    def test_update_artefactlist_update_existing(self):
        testFilePath = os.path.join(self.sessionDir, "test1.avid")
        fileHelper.save_artefacts_to_xml(testFilePath, self.data, rootPath=self.testDataDir)

        fileHelper.update_artefactlist(testFilePath, self.data_simelar, update_existing=True, rootPath=self.testDataDir)

        artefacts = fileHelper.load_artefact_collection_from_xml(os.path.join(self.sessionDir, "test1.avid"),
                                                                 rootPath=self.testDataDir)
        referenceArtefacts = [self.a1, self.a2, self.a3_update, self.a4]
        self.assertEqual(artefacts, referenceArtefacts)

        fileHelper.save_artefacts_to_xml(testFilePath, self.data, savePathsRelative=False)

        fileHelper.update_artefactlist(testFilePath, self.data_simelar, update_existing=True, savePathsRelative=False)

        artefacts = fileHelper.load_artefact_collection_from_xml(os.path.join(self.sessionDir, "test1.avid"))
        referenceArtefacts = [self.a1, self.a2, self.a3_update, self.a4]
        self.assertEqual(artefacts, referenceArtefacts)

    def test_update_artefactlist_waitfail(self):
        testFilePath = os.path.join(self.sessionDir, "test1.avid")
        fileHelper.save_artefacts_to_xml(testFilePath, self.data, rootPath=self.testDataDir)

        lf_path = testFilePath + os.extsep + 'update_lock'
        with open(lf_path, 'x') as lf:
            lf.write('dummy lock')

        access_denied = False
        try:
            fileHelper.update_artefactlist(testFilePath, self.data_simelar, rootPath=self.testDataDir, wait_time=1)
        except PermissionError:
            access_denied = True

        self.assertTrue(access_denied)

    def test_update_artefactlist_waitsuccess(self):

        testFilePath = os.path.join(self.sessionDir, "test1.avid")
        fileHelper.save_artefacts_to_xml(testFilePath, self.data, rootPath=self.testDataDir)

        lf_path = testFilePath + os.extsep + 'update_lock'
        with open(lf_path, 'x') as lf:
            lf.write('dummy lock')

        # trigger the process that will remove the lock in 2 sec to check if update_artefactlist will then work properly
        t = threading.Thread(target=remove_lock_file, args=(lf_path,))
        t.start()

        fileHelper.update_artefactlist(testFilePath, self.data_simelar, rootPath=self.testDataDir)
        t.join()


if __name__ == "__main__":
    unittest.main()
