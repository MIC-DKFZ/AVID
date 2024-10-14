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
import logging
import os
import uuid
from builtins import object
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from avid.actions.cliActionBase import CLIActionBase
from avid.common import osChecker

logger = logging.getLogger(__name__)

def process_batch(action_batch):
    global logger

    (batch_uid, batch_nr, actions) = action_batch

    logger.debug(f'Process action batch #{batch_nr}. UID: {batch_uid}')

    actions_to_process = list()
    for action in actions:
        if action.do_setup():
            actions_to_process.append(action)
    if len(actions_to_process)>0:
        # get the CLIConnector of the actions (we assume that all actions have the same CLIEvecutor as BatchActions
        # use the same CLIConnector for all generated actions.
        cli_connector = actions_to_process[0]._cli_connector
        action_tag = actions_to_process[0]._actionTag

        # generate the cli script for the whole batch
        batch_call_content=''
        modified_call_prefix=''
        if osChecker.isWindows():
            modified_call_prefix = 'call '

        for action in actions_to_process:
            # add piping for the logs of one action
            modified_call = f'{modified_call_prefix}{action._last_cli_call} > {action._last_log_file_path}' \
                            f' 2> {action._last_log_error_file_path}\n'
            batch_call_content = batch_call_content + modified_call

        # generate the file paths
        path = Path(actions_to_process[0]._last_cli_call)
        batch_cli_path_base = path.parent/f'batch_{action_tag}_{batch_uid}_{batch_nr}'

        batch_cli_call=cli_connector.generate_cli_file(str(batch_cli_path_base), batch_call_content)
        batch_log_file_path = batch_cli_call + os.extsep + "log"
        batch_log_error_file_path = batch_cli_call + os.extsep + "error.log"

        # We don't use action.do_process (which just make the call to cli_connector_execute()
        # We use the cli_connector directly to inject the generated batch cli call
        try:
            cli_connector.execute(batch_cli_call, log_file_path=batch_log_file_path,
                                  error_log_file_path=batch_log_error_file_path,
                                  cwd=actions_to_process[0]._cwd)
        except BaseException as e:
            logger.warning(f'Error occurred while CLIBatchScheduler processed a batch.'
                           f'Check the action states. Some actions might have failed.'
                           f' Failed batch script: "{batch_cli_call}. Error details: {str(e)}')
            for action in actions_to_process:
                action._reportWarning(f'Error occurred while CLIBatchScheduler processed thw batch containing this action.'
                                      f'Check the action state. Action might have failed, but problem could also have been'
                                      f'by another action. Failed batch script: "{batch_cli_call}. Error details: {str(e)}')

    for action in actions:
        action.do_finalize()


class CLIBatchScheduler(object):
    """Scheduler class that can be used with action based on CLIActionBase. Purpose of the scheduler to allow processing
       the processing step of a batch of actions in one batch file instead of calling each action on its own.
       This can e.g. be used in conjunction with external scheduling systems (e.g. LSF cliConnectors) to submit not
       each action as a lsf job, but a batch of actions as one LSF job."""
    def __init__(self, batch_size, thread_count=1):
        self.batch_size = batch_size
        self.thread_count = thread_count

    def execute(self, action_list):
        # check if all actions derive from CLIActionBase
        wrong_action = next((action for action in action_list if not isinstance(action, CLIActionBase)), None)
        if wrong_action:
            raise RuntimeError('Wrong usage of cliBatchScheduler. cliBatchScheduler can only used together with action'
                               'classes derived from CLIActionBase. Please check your workflow code. First wrong action'
                               f'instance: {wrong_action}')

        batch_uid = uuid.uuid4()

        # split action in batches
        action_batches = [action_list[i:i + self.batch_size] for i in range(0, len(action_list), self.batch_size)]
        action_batches = [(batch_uid, i[0], i[1]) for i in enumerate(action_batches)] # populate the list with additional
                                                                                # information

        thread_count = min(self.thread_count, len(action_batches))

        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            executor.map(process_batch, action_batches)