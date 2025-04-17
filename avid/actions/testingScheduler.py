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

from avid.actions.simpleScheduler import SimpleScheduler

class TestingScheduler:
    """
    A helper scheduler for testing purposes that wraps a different scheduler and only passes on a specified number of
    actions. All the other actions are filtered out and will neither be skipped nor failed.
    :param scheduler: The primary scheduler that is to be wrapped. Needs to provide the method .execute(actionList)
    :param action_limit: The number of actions that should be passed through to the scheduler. (default: 10)
    """

    def __init__(self, scheduler=SimpleScheduler(), action_limit=10):
        self.scheduler = scheduler
        self.action_limit = action_limit

    def execute(self, actionList):
        self.scheduler.execute(actionList[:self.action_limit])
