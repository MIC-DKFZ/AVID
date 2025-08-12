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
import shutil
import unittest
import os
import avid.common.artefact.generator as artefactGenerator
from avid.common.artefact import getArtefactProperty
from avid.actions.dummy import DummyCLIAction as DummyAction
import avid.common.workflow as workflow
import avid.common.artefact.defaultProps as artefact_props
from avid.actions.cliBatchScheduler import CLIBatchScheduler

class TestCLIBatchScheduler(unittest.TestCase):
    def setUp(self):
        self.sessionDir = os.path.join(os.path.split(__file__)[0],"temporary_test_CLIBatchScheduler")
        self.testDataDir = os.path.join(os.path.split(__file__)[0],"data")

        self.session = workflow.Session("session1", self.sessionDir)
        workflow.currentGeneratedSession =self.session
        self.artefact = list()
        self.actions = list()

        for i in range(0, 15):
            a = artefactGenerator.generateArtefactEntry("Case1", None, i, "Action1", "result", "dummy", os.path.join(self.testDataDir, "artefact1.txt"))
            self.session.add_artefact(a)
            self.actions.append(DummyAction([a],actionTag="Action1"))

    def tearDown(self):
      try:
        shutil.rmtree(self.sessionDir)
      except:
        pass

    def test_Scheduler(self):
        scheduler = CLIBatchScheduler(5)
        scheduler.execute(self.actions)

        for action in self.actions:
            self.assertTrue(action.isSuccess)
            self.assertFalse(getArtefactProperty(action.outputArtefacts[0],artefact_props.INVALID))

        self.assertEqual(len(self.session.executed_actions), len(self.actions))
        self.assertEqual(len(self.session.getFailedActions()), 0)
        self.assertEqual(len(self.session.getSkippedActions()), 0)
        self.assertEqual(len(self.session.getSuccessfulActions()), len(self.actions))

        self.session.executed_actions.clear()
        scheduler.execute(self.actions)

        for action in self.actions:
            self.assertTrue(action.isSkipped)

        self.assertEqual(len(self.session.executed_actions), len(self.actions))
        self.assertEqual(len(self.session.getFailedActions()), 0)
        self.assertEqual(len(self.session.getSkippedActions()), len(self.actions))
        self.assertEqual(len(self.session.getSuccessfulActions()), 0)

    def test_Scheduler_always_do(self):
        for action in self.actions:
            action._alwaysDo = True

        scheduler = CLIBatchScheduler(5)
        scheduler.execute(self.actions)

        for action in self.actions:
            self.assertTrue(action.isSuccess)
            self.assertFalse(getArtefactProperty(action.outputArtefacts[0],artefact_props.INVALID))

        self.assertEqual(len(self.session.executed_actions), len(self.actions))
        self.assertEqual(len(self.session.getFailedActions()), 0)
        self.assertEqual(len(self.session.getSkippedActions()), 0)
        self.assertEqual(len(self.session.getSuccessfulActions()), len(self.actions))

        self.session.executed_actions.clear()
        scheduler.execute(self.actions)

        for action in self.actions:
            self.assertTrue(action.isSuccess)

        self.assertEqual(len(self.session.executed_actions), len(self.actions))
        self.assertEqual(len(self.session.getFailedActions()), 0)
        self.assertEqual(len(self.session.getSkippedActions()), 0)
        self.assertEqual(len(self.session.getSuccessfulActions()), len(self.actions))

    def test_Scheduler_threaded(self):
        scheduler = CLIBatchScheduler(4,3)
        scheduler.execute(self.actions)

        for action in self.actions:
            self.assertTrue(action.isSuccess)
            self.assertFalse(getArtefactProperty(action.outputArtefacts[0],artefact_props.INVALID))

        self.assertEqual(len(self.session.executed_actions), len(self.actions))
        self.assertEqual(len(self.session.getFailedActions()), 0)
        self.assertEqual(len(self.session.getSkippedActions()), 0)
        self.assertEqual(len(self.session.getSuccessfulActions()), len(self.actions))

        self.session.executed_actions.clear()
        scheduler.execute(self.actions)

        for action in self.actions:
            self.assertTrue(action.isSkipped)

        self.assertEqual(len(self.session.executed_actions), len(self.actions))
        self.assertEqual(len(self.session.getFailedActions()), 0)
        self.assertEqual(len(self.session.getSkippedActions()), len(self.actions))
        self.assertEqual(len(self.session.getSuccessfulActions()), 0)

    def test_Scheduler_threaded_always_do(self):
        for action in self.actions:
            action._alwaysDo = True

        scheduler = CLIBatchScheduler(4,3)
        scheduler.execute(self.actions)

        for action in self.actions:
            self.assertTrue(action.isSuccess)
            self.assertFalse(getArtefactProperty(action.outputArtefacts[0],artefact_props.INVALID))

        self.assertEqual(len(self.session.executed_actions), len(self.actions))
        self.assertEqual(len(self.session.getFailedActions()), 0)
        self.assertEqual(len(self.session.getSkippedActions()), 0)
        self.assertEqual(len(self.session.getSuccessfulActions()), len(self.actions))

        self.session.executed_actions.clear()
        scheduler.execute(self.actions)

        for action in self.actions:
            self.assertTrue(action.isSuccess)

        self.assertEqual(len(self.session.executed_actions), len(self.actions))
        self.assertEqual(len(self.session.getFailedActions()), 0)
        self.assertEqual(len(self.session.getSkippedActions()), 0)
        self.assertEqual(len(self.session.getSuccessfulActions()), len(self.actions))

    def test_Scheduler_skipping(self):
        scheduler = CLIBatchScheduler(2)

        skip_pattern = [2, 5, 6, 7, 9, 10]
        for action in [self.actions[i] for i in skip_pattern]:
            action.will_skip = True

        scheduler.execute(self.actions)

        for (pos, action) in enumerate(self.actions):
            if pos in skip_pattern:
                self.assertTrue(action.isSkipped)
                self.assertFalse(getArtefactProperty(action.outputArtefacts[0],artefact_props.INVALID))
            else:
                self.assertTrue(action.isSuccess)
                self.assertFalse(getArtefactProperty(action.outputArtefacts[0],artefact_props.INVALID))

        self.assertEqual(len(self.session.executed_actions), len(self.actions))
        self.assertEqual(len(self.session.getFailedActions()), 0)
        self.assertEqual(len(self.session.getSkippedActions()), len(skip_pattern))
        self.assertEqual(len(self.session.getSuccessfulActions()), len(self.actions)-len(skip_pattern))

    def test_Scheduler_failing(self):
        scheduler = CLIBatchScheduler(2)

        fail_pattern = [2, 5, 6, 7, 9, 10]
        for action in [self.actions[i] for i in fail_pattern]:
            action.will_fail = True

        scheduler.execute(self.actions)

        for (pos, action) in enumerate(self.actions):
            if pos in fail_pattern:
                self.assertTrue(action.isFailure)
                self.assertTrue(getArtefactProperty(action.outputArtefacts[0],artefact_props.INVALID))
            else:
                self.assertTrue(action.isSuccess)
                self.assertFalse(getArtefactProperty(action.outputArtefacts[0],artefact_props.INVALID))

        self.assertEqual(len(self.session.executed_actions), len(self.actions))
        self.assertEqual(len(self.session.getFailedActions()), len(fail_pattern))
        self.assertEqual(len(self.session.getSkippedActions()), 0)
        self.assertEqual(len(self.session.getSuccessfulActions()), len(self.actions)-len(fail_pattern))

    def test_Scheduler_skipped_failing(self):
        scheduler = CLIBatchScheduler(2)

        skip_pattern = [2, 6, 7, 9, 11]
        fail_pattern = [5, 8, 12,13]
        for action in [self.actions[i] for i in skip_pattern]:
            action.will_skip = True
        for action in [self.actions[i] for i in fail_pattern]:
            action.will_fail = True

        scheduler.execute(self.actions)

        for (pos, action) in enumerate(self.actions):
            if pos in fail_pattern:
                self.assertTrue(action.isFailure)
                self.assertTrue(getArtefactProperty(action.outputArtefacts[0],artefact_props.INVALID))
            elif pos in skip_pattern:
                self.assertTrue(action.isSkipped)
                self.assertFalse(getArtefactProperty(action.outputArtefacts[0], artefact_props.INVALID))
            else:
                self.assertTrue(action.isSuccess)
                self.assertFalse(getArtefactProperty(action.outputArtefacts[0],artefact_props.INVALID))

        self.assertEqual(len(self.session.executed_actions), len(self.actions))
        self.assertEqual(len(self.session.getFailedActions()), len(fail_pattern))
        self.assertEqual(len(self.session.getSkippedActions()), len(skip_pattern))
        self.assertEqual(len(self.session.getSuccessfulActions()), len(self.actions)-
                         (len(fail_pattern)+len(skip_pattern)))

if __name__ == '__main__':
    unittest.main()