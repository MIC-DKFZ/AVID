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
from avid.common.workflow.structure_definitions import loadStructurDefinition_xml as load_xml

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