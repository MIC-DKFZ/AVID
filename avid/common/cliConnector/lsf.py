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
import subprocess
import time
from pathlib import Path

from avid.common import osChecker
from avid.common.cliConnector import URLMappingCLIConnectorBase, DefaultCLIConnector

logger = logging.getLogger(__name__)


class LSFCLIConnector(URLMappingCLIConnectorBase):
    """Implementation that allows to execute an action on an lsf cluster."""

    def __init__(self, mount_map=None, additional_bsub_arguments=None):
        """:param mount_map: Dictionary that contains the mapping between relevant paths
         outside of the container (those stored in the session) and the pathes that will
         be known in the container. Needed to properly convert artefact urls.
         Key of the map is the mount path inside of the container, the value is the respective
         path outside.
         :param additional_bsub_arguments: List of additional arguments that will be added to the bsub
         call directly after the cli_path.
         "bsub <clipath> [<additional_bsub_arguments>] [-o <log_file>] [-e <error_log_file>]."""
        super().__init__(mount_map)
        self.additional_bsub_arguments = additional_bsub_arguments
        pass

    @staticmethod
    def generate_lsf_log_file_path(log_file_path):
        path = Path(log_file_path)
        file_extension = path.suffixe()
        file_stem = log_file_path[:-len(file_extension)]

        return file_stem+'.lsf'+file_extension

    def execute(self, cli_file_path, log_file_path=None, error_log_file_path=None, cwd=None):
        global logger

        lsf_logfile = None

        if log_file_path is not None:
            lsf_path = LSFCLIConnector.generate_lsf_log_file_path(log_file_path)
            try:
                lsf_logfile = open(lsf_path, "w")
            except:
                lsf_logfile = None
                logger.debug('Unable to generate lsf log file (%s) for call: %s', lsf_path, cli_file_path)

        lsf_error_logfile = None

        if error_log_file_path is not None:
            lsf_path = LSFCLIConnector.generate_lsf_log_file_path(error_log_file_path)
            try:
                lsf_error_logfile = open(lsf_path, "w")
            except:
                lsf_error_logfile = None
                logger.debug('Unable to generate lsf error log file (%s) for call: %s', lsf_path, cli_file_path)

        try:
            DefaultCLIConnector.ensure_file_availability(cli_file_path)

            run_arg = ['bsub', cli_file_path]

            if self.additional_bsub_arguments:
                run_arg.extend(self.additional_bsub_arguments)

            if log_file_path is not None:
                run_arg.append('-o')
                run_arg.append(log_file_path)

            if error_log_file_path is not None:
                run_arg.append('-e')
                run_arg.append(error_log_file_path)

            use_shell = not osChecker.isWindows()
            run_result = subprocess.run(run_arg, capture_output=True, text=True, shell=use_shell)
            # Assuming job ID is in the format "Job <job_id> is submitted ..."
            job_id_line = run_result.stdout.strip()
            job_id = job_id_line.split()[1].strip('<>').strip()

            if lsf_logfile is not None:
                lsf_logfile.write(run_result.stdout)
                lsf_logfile.write('\n Job process: ')

            if lsf_error_logfile is not None and run_result.stderr:
                lsf_error_logfile.write(run_result.stderr)

            # now wait for the lsf job to be finished
            is_running = True
            is_successful = False
            wait_rounds = 0
            while not is_running:
                if lsf_logfile is not None and wait_rounds%10==0:
                    lsf_logfile.write('.')

                time.sleep(1)  # Wait befor checking again

                status_result = subprocess.run(['bjobs', job_id], capture_output=True, text=True)

                if lsf_error_logfile is not None and run_result.stderr:
                    lsf_error_logfile.write(run_result.stderr)

                is_running = "RUN" in status_result.stdout or "PEND" in status_result.stdout

                is_successful = "DONE" in status_result.stdout

                if not is_running and lsf_logfile is not None and run_result.stdcout:
                    lsf_logfile.write('\n\n')
                    lsf_logfile.write(run_result.stdcout)

            if is_successful:
                logger.debug('Call "%s" finished normally', cli_file_path)
                if lsf_logfile is not None:
                    lsf_logfile.write('\n\nJob finished normally.')
            else:
                logger.error('Call "%s" failed or was suspended', cli_file_path)
                if lsf_logfile is not None:
                    lsf_logfile.write('\n\nERROR: Job failed or was suspended/killed.')

        finally:
            if lsf_logfile is not None:
                lsf_logfile.close()
            if lsf_error_logfile is not None:
                lsf_error_logfile.close()
