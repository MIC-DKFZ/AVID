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

import avid.externals.virtuos as virtuos


class TestVirtuosPlanManipulation(unittest.TestCase):

    def setUp(self):
        self.testDataDir = os.path.join(
            os.path.split(__file__)[0], "data", "externals", "virtuos"
        )
        self.rootTestDir = os.path.join(os.path.split(__file__)[0], "temporary")
        self.sessionDir = os.path.join(
            os.path.split(__file__)[0], "temporary", "test_externals_virtuos"
        )

        try:
            os.makedirs(self.sessionDir)
        except:
            pass

    def tearDown(self):
        try:
            shutil.rmtree(self.rootTestDir)
        except:
            pass

    def test_get_value(self):

        plan = virtuos.readFile(os.path.join(self.testDataDir, "reference_plan.pln"))

        self.assertEqual(
            virtuos.getValueFromPlan(plan, virtuos.KEY_PATIENT_NAME), "DOE091,JOHN"
        )
        self.assertEqual(
            virtuos.getValueFromPlan(plan, virtuos.KEY_CREATED_BY), "VIRTUOS 4.6.10"
        )
        self.assertEqual(
            virtuos.getValueFromPlan(plan, virtuos.KEY_CREATED_ON),
            "Fri Mar  4 00:11:22 1900",
        )
        self.assertEqual(
            virtuos.getValueFromPlan(plan, virtuos.KEY_DOSE_CALC_BASE),
            "0000000003_TEST_DOE103.ctx",
        )
        self.assertEqual(
            virtuos.getValueFromPlan(plan, virtuos.KEY_DOSE_CALC_BY),
            "dc09: 0.9-18 [calc. mode 4]",
        )
        self.assertEqual(
            virtuos.getValueFromPlan(plan, virtuos.KEY_DOSE_CALC_ON),
            "Fri Mar  4 00:11:22 1900",
        )
        self.assertEqual(
            virtuos.getValueFromPlan(plan, virtuos.KEY_DOSE_FILE),
            "0000000003_TEST_DOE103.dos",
        )
        self.assertEqual(
            virtuos.getValueFromPlan(plan, virtuos.KEY_MONITOR_UNITS), "30000.00"
        )
        self.assertEqual(
            virtuos.getValueFromPlan(plan, virtuos.KEY_NORM_DOSE), "900.00"
        )
        self.assertEqual(
            virtuos.getValueFromPlan(plan, virtuos.KEY_NUM_FRACTIONS), "28"
        )
        self.assertEqual(
            virtuos.getValueFromPlan(plan, virtuos.KEY_PRESCRIBED_DOSE), "50.40"
        )
        self.assertEqual(
            virtuos.getValueFromPlan(plan, virtuos.KEY_REL_REF_DOSE), "1.5"
        )

    def test_plan_reset(self):
        resetRefPlan = virtuos.readFile(
            os.path.join(self.testDataDir, "reset_plan.pln")
        )

        testPlanPath = os.path.join(self.sessionDir, "test.pln")
        shutil.copyfile(
            os.path.join(self.testDataDir, "reference_plan.pln"), testPlanPath
        )

        virtuos.resetPlanFile(testPlanPath)

        testPlan = virtuos.readFile(testPlanPath)

        self.assertEqual(resetRefPlan, testPlan)

    def test_plan_normalization(self):
        testPlanPath = os.path.join(self.sessionDir, "test.pln")
        shutil.copyfile(
            os.path.join(self.testDataDir, "reference_plan_2.pln"), testPlanPath
        )

        virtuos.normalizePlanFile(
            testPlanPath, os.path.join(self.testDataDir, "reference_plan.pln")
        )

        plan = virtuos.readFile(testPlanPath)
        norm_dose = virtuos.getValueFromPlan(plan, virtuos.KEY_NORM_DOSE)

        self.assertEqual(float(norm_dose), 1800)

    def test_calculate_norm_dose_correction(self):
        # @TODO
        pass


if __name__ == "__main__":
    unittest.main()
