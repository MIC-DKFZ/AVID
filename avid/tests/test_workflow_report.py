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
import avid.common.artefact.generator as artefactGenerator
from avid.actions.dummy import DummyCLIAction as DummyAction
import avid.common.workflow as workflow
from avid.actions.simpleScheduler import SimpleScheduler
from avid.common.workflow.report import create_actions_report


class TestWorkflowReport(unittest.TestCase):
    def setUp(self):
        self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_workflow_report")
        self.testDataDir = os.path.join(os.path.split(__file__)[0],"data")

        self.session = workflow.Session("session1", self.sessionDir)
        workflow.currentGeneratedSession =self.session
        self.artefact = list()
        self.actions_success = list()
        self.actions_skipped = list()
        self.actions_failed = list()

        for i in range(0, 3):
            a = artefactGenerator.generateArtefactEntry("Case1", None, i, "Action1", "result", "dummy", os.path.join(self.testDataDir, "artefact1.txt"))
            self.session.addArtefact(a)
            self.actions_success.append(DummyAction([a],actionTag="ActionSuccess"))
            self.actions_skipped.append(DummyAction([a],actionTag="ActionSkipped",will_skip=True))
            self.actions_failed.append(DummyAction([a],actionTag="ActionFailed",will_fail=True))

        self.actions = self.actions_success+self.actions_skipped+self.actions_failed

    def test_create_actions_report(self):
        scheduler = SimpleScheduler()
        scheduler.execute(self.actions)
        report_file_path = os.path.join(self.sessionDir,'report.txt')
        create_actions_report(actions=self.actions, report_file_path=report_file_path)

        self.assertTrue(os.path.exists(report_file_path))

        report_file_2_path = os.path.join(self.sessionDir,'report.zip')
        create_actions_report(actions=self.actions, report_file_path=report_file_2_path, generate_report_zip=True)

        self.assertTrue(os.path.exists(report_file_2_path))

if __name__ == '__main__':
    unittest.main()