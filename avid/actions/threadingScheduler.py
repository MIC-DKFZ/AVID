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

import queue
from builtins import object, range
from threading import Thread


class Worker(Thread):
    def __init__(self, actions):
        Thread.__init__(self)
        self.actions = actions
        self.daemon = True
        self.start()

    def run(self):
        try:
            while True:
                action = self.actions.get()
                action.do()
                self.actions.task_done()
        except queue.Empty:
            pass


class ThreadingScheduler(object):
    """Simple threaded scheduler that processes the actions via a thread pool."""

    def __init__(self, threadcount):
        self.threadcount = threadcount

    def execute(self, actionList):

        actionqueue = queue.Queue()

        threadcount = self.threadcount
        if threadcount > len(actionList):
            threadcount = len(actionList)

        for action in actionList:
            actionqueue.put(action)

        for i in range(threadcount):
            w = Worker(actionqueue)

        actionqueue.join()
