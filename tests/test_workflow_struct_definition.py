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

from avid.common.workflow.structure_definitions import \
    loadStructurDefinition_xml as load_xml


class TestStructDefinitionHelper(unittest.TestCase):

    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data")
      self.testfile = os.path.join(self.testDataDir, "structdef.xml")
      self.invalidtestfile = os.path.join(self.testDataDir, "testlist.avid")
              
    def tearDown(self):
      pass

    def test_load_xml(self):
      
      structdefs = load_xml(self.testfile)    
      
      self.assertListEqual(sorted(structdefs.keys()), sorted(["Gehirn","PTV"]))
      self.assertEqual(structdefs["Gehirn"], "Gehirn|GEHIRN|Brain")
      self.assertEqual(structdefs["PTV"], None)

    def test_load_invalids(self):
      
      with self.assertRaises(ValueError):
        load_xml("none-existing-file")
      
      with self.assertRaises(ValueError):
        load_xml(self.invalidtestfile)

if __name__ == "__main__":
    unittest.main()