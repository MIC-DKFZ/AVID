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

from avid.common.workflow import initSession
from avid.common.workflow.structure_definitions import loadStructurDefinition_xml as load_xml

class TestStructDefinitionHelper(unittest.TestCase):

    def setUp(self):
        self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_workflow")
        self.testDataDir = os.path.join(os.path.split(__file__)[0],"data")
        self.bootstrapFile = os.path.join(self.testDataDir, "testlist.avid")
              
    def tearDown(self):
        try:
            shutil.rmtree(self.sessionDir)
        except:
            pass

    def test_initSession(self):
        session = initSession(os.path.join(self.sessionDir, "test.avid"))
        session = initSession(os.path.join(self.sessionDir, "test_noLogging.avid"), initLogging=False)
        session = initSession(os.path.join(self.sessionDir, "test_bootstrap.avid"), expandPaths=True, bootstrapArtefacts=self.bootstrapFile)

if __name__ == "__main__":
    unittest.main()