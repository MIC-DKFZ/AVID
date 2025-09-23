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
import unittest

import avid.common.artefact.generator as artefactGenerator
import avid.common.workflow as workflow
from avid.actions.dummy import DummySingleAction as DummyAction
from avid.actions.simpleScheduler import SimpleScheduler
from avid.actions.testingScheduler import TestingScheduler


class TestTestingScheduler(unittest.TestCase):
    def setUp(self):
        self.sessionDir = os.path.join(
            os.path.split(__file__)[0], "temporary_test_actions"
        )
        self.testDataDir = os.path.join(os.path.split(__file__)[0], "data")

        self.session = workflow.Session("session1", self.sessionDir)
        self.actions = list()

        for i in range(6):
            a = artefactGenerator.generateArtefactEntry(
                "Case1",
                None,
                i,
                "Action1",
                "result",
                "dummy",
                os.path.join(self.testDataDir, "artefact1.txt"),
            )
            self.session.add_artefact(a)
            self.actions.append(
                DummyAction(
                    [a], actionTag="Action1", session=self.session, alwaysDo=True
                )
            )

    def test_Scheduler(self):
        scheduler = TestingScheduler(SimpleScheduler(), action_limit=2)
        scheduler.execute(self.actions)

        self.assertEqual(len(self.session.executed_actions), 2)
        self.assertEqual(len(self.session.getSuccessfulActions()), 2)
        self.assertEqual(len(self.session.getFailedActions()), 0)
        self.assertEqual(len(self.session.getSkippedActions()), 0)

        self.session.executed_actions.clear()

        scheduler = TestingScheduler(action_limit=4)
        scheduler.execute(self.actions)

        self.assertEqual(len(self.session.executed_actions), 4)
        self.assertEqual(len(self.session.getSuccessfulActions()), 4)
        self.assertEqual(len(self.session.getFailedActions()), 0)
        self.assertEqual(len(self.session.getSkippedActions()), 0)


if __name__ == "__main__":
    unittest.main()
