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

import unittest
import os
import shutil
import avid.externals.doseTool as dosetool

class TestDoseTool(unittest.TestCase):

    def setUp(self):
      self.testDataDir = os.path.join(os.path.split(__file__)[0],"data", "doseStatsCollectorTest")
      self.testArtefactFile = os.path.join(os.path.split(__file__)[0],"data", "doseStatsCollectorTest", "dose_stat_0_0_0.xml")
      self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary","test_doseStatsCollector")
      self.tempRoot = os.path.join(os.path.split(__file__)[0],"temporary")
      
              
    def tearDown(self):
      try:
        shutil.rmtree(self.tempRoot)
      except:
        pass


    def test_DoseProperty(self):
      
      prop = dosetool.DoseProperty()
      
      prop.attributes["b"] = "foo"
      prop.attributes["a"] = "bar"
      prop.attributes[dosetool.XML_ATTR_NAME] = "prop1"
      
      self.assertEqual(prop.name, "prop1")
      self.assertEqual(prop.fullname, "prop1_a=bar_b=foo")


    def test_loadResult(self):
      
      result = dosetool.loadResult(self.testArtefactFile)
             
      self.assertEqual(result.config[dosetool.XML_DOSE_FILE], "testdose.mhd")
      self.assertEqual(result.config[dosetool.XML_DOSE_ID], "9iwdei32i3ejkewk")
      self.assertEqual(result.config[dosetool.XML_REQUESTED_STRUCT_REGEX], "[Nose|nose|NOSE]")
      self.assertEqual(result.config[dosetool.XML_STRUCT_FILE], "teststruct.dcm")
      self.assertEqual(result.config[dosetool.XML_STRUCT_NAME], "Nose")

      prop = result.getProperty("volume", unkown = "True")
      self.assert_(prop is None)

      prop = result.getProperty("unkown")
      self.assert_(prop is None)

      prop = result.getProperty("volume")
      self.assert_(prop is not None)
      self.assertEqual(prop.name, "volume")
      self.assertEqual(prop.fullname, "volume")
      self.assertEqual(prop.value, "13.15900235728852")

      prop = result.getProperty("maximum")
      self.assert_(prop is not None)
      self.assertEqual(prop.name, "maximum")
      self.assertEqual(prop.fullname, "maximum")
      self.assertEqual(prop.value, "1.598613235583097")

      prop = result.getProperty("Dx_x=5")
      self.assert_(prop is not None)
      self.assertEqual(prop.name, "Dx")
      self.assertEqual(prop.fullname, "Dx_x=5")
      self.assertEqual(prop.value, "0.1736000031232834")


if __name__ == "__main__":
    unittest.main()