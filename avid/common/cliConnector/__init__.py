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
import math
import os
import stat
import subprocess
import time

from avid.common import osChecker, AVIDUrlLocater
import avid.common.config_mangager as AVIDConfigManager
import avid.common.artefact as artefactHelper
import avid.common.artefact.defaultProps as artefactProps

logger = logging.getLogger(__name__)

def default_artefact_url_extraction_delegate(arg_name, arg_value):
    """Default implementation of the extraction of the urls of a passed list of artefacts.
       It just retrieves the URL of each artefact and passes it back.
       :param arg_name: Name/id of the argument
       :param arg_value: list of artefacts that are associated with the argument.
       :return: Returns the list of urls that are associated with the argument (its artefacts)."""
    result = list()
    for artefact in arg_value:
        artefactPath = artefactHelper.getArtefactProperty(artefact, artefactProps.URL)
        result.append(artefactPath)
    return result

class DefaultCLIConnector(object):
    """Default implementation of a CLI connector. It is used to abstract between the action logic and the system
     specific peculiarities for cli the execution (e.g. direct cli call or a call via a container)."""

    def __init__(self):
        pass

    def get_artefact_url_extraction_delegate(self, action_extraction_delegate=None):
        """Returns the URL extraction delegate that should be used when working with the connector.
        :param action_extraction_delegate: If the actions specifies its own delegate it can be passed
        and will be wrapped accordingly."""
        if action_extraction_delegate is not None:
            return action_extraction_delegate
        else:
            return default_artefact_url_extraction_delegate

    def get_executable_url(self, workflow, actionID, actionConfig = None):
        """Returns url+executable for a tool_id request that should be used in the cli file. This serves as an
        abstraction, in order to allow the connector to change the deduction strategy for the executable url.
        Default implementation just uses the AVIDUrlLocater.
        :param workflow: session instance that should be used for deducing the executable url
        :param actionID: tool_id of the action that requests the URL
        :param actionConfig: action_config specifies if a certain configuration of an action should be used."""
        return AVIDUrlLocater.get_tool_executable_url(workflow=workflow, tool_id=actionID, action_config=actionConfig)

    def generate_cli_file(self, file_path_base, content):
        """Function generates the CLI file based on the passed file name base (w/o extension, extension will be added)
         and the content. It returns the full path to the CLI file."""
        global logger

        if osChecker.isWindows():
            file_name = file_path_base + os.extsep + 'bat'
        else:
            file_name = file_path_base + os.extsep + 'sh'

        path = os.path.split(file_name)[0]

        try:
            osChecker.checkAndCreateDir(path)
            with open(file_name, "w") as outputFile:
                outputFile.write(content)
                outputFile.close()

            if not osChecker.isWindows():
                st = os.stat(file_name)
                os.chmod(file_name, st.st_mode | stat.S_IXUSR)

        except:
            logger.error("Error when writing cli script. Location: %s.", file_name)
            raise

        return file_name

    @staticmethod
    def ensure_file_availability(cli_file_path):
        """Helper used to enusre that a generated cli file is accessable for the execution."""
        if os.path.isfile(cli_file_path):
            # Fix for T20136. Unsatisfying solution, but found no better way on
            # windows. If you make the subprocess calls to batch files (thats the
            # reason for the isfile() check) directly you get random "Error 32"
            # file errors (File already opened by another process) caused
            # by opening the bat files, which are normally produced by the actions.
            # "os.rename" approach was the simpliest way to check os independent
            # if the process can access the bat file or if there is still a racing
            # condition.
            pause_duration = AVIDConfigManager.get_setting(AVIDConfigManager.SETTING_NAMES.ACTION_SUBPROCESS_PAUSE)
            max_pause_count = math.ceil(AVIDConfigManager.get_setting(AVIDConfigManager.SETTING_NAMES.ACTION_TIMEOUT)
                                        / pause_duration)
            pause_count = 0
            time.sleep(0.1)
            while True:
                try:
                    os.rename(cli_file_path, cli_file_path)
                    break
                except OSError:
                    if pause_count < max_pause_count:
                        time.sleep(pause_duration)
                        pause_count = pause_count + 1
                        logger.debug('"%s" is not accessible. Wait and try again.', cli_file_path)
                    else:
                        break

    def execute(self, cli_file_path, log_file_path=None, error_log_file_path=None, cwd=None):
        global logger

        logfile = None

        if log_file_path is not None:
            try:
                logfile = open(log_file_path, "w")
            except:
                logfile = None
                logger.debug('Unable to generate log file for call: %s', cli_file_path)

        errlogfile = None

        if error_log_file_path is not None:
            try:
                errlogfile = open(error_log_file_path, "w")
            except:
                errlogfile = None
                logger.debug('Unable to generate error log file for call: %s', cli_file_path)

        try:
            returnValue = 0

            DefaultCLIConnector.ensure_file_availability(cli_file_path)

            useShell = not osChecker.isWindows()
            if cwd is None:
                returnValue = subprocess.call(cli_file_path, stdout=logfile, stderr=errlogfile, shell=useShell)
            else:
                returnValue = subprocess.call(cli_file_path, cwd=cwd, stdout=logfile, stderr=errlogfile, shell=useShell)

            if returnValue == 0:
                logger.debug('Call "%s" finished and returned %s', cli_file_path, returnValue)
            else:
                logger.error('Call "%s" finished and returned %s', cli_file_path, returnValue)

        finally:
            if logfile is not None:
                logfile.close()
            if errlogfile is not None:
                errlogfile.close()


class URLMappingCLIConnectorBase(DefaultCLIConnector):
    """Base Implementation for CLIConnectors that allow the mapping of URLs (e.g. for container connectors)."""

    def __init__(self, mount_map = None):
        """
        :param mount_map: Dictionary that contains the mapping between relevant paths
            outside of the container (those stored in the session) and the pathes that will
            be known in the container. Needed to properly convert artefact urls.
            Key of the map is the mount path inside of the container, the value is the respective
            path outside.
         """
        super().__init__()
        self.mount_map=mount_map
        if self.mount_map is None:
            self.mount_map = dict()
        pass

    @staticmethod
    def apply_mount_map(mount_map, filepath):
        mappedPath = filepath

        for mountPath in mount_map:
            try:
                if filepath.find(mount_map[mountPath])==0:
                    mappedPath = mappedPath.replace(mount_map[mountPath], mountPath)
                    break
            except Exception:
                pass
        return mappedPath

    def get_artefact_url_extraction_delegate(self, action_extraction_delegate=None):
        """Returns the URL extraction delegate that should be used when working with the connector.
        :param action_extraction_delegate: If the actions specifies its own delegate it can be passed
        and will be wrapped accordingly."""

        if action_extraction_delegate is None:
            action_extraction_delegate = default_artefact_url_extraction_delegate

        def extractionWrapper(arg_name, arg_value):
            results = action_extraction_delegate(arg_name, arg_value)

            mappedResults = list()
            for result in results:
                mappedResults.append(URLMappingCLIConnectorBase.apply_mount_map(mount_map=self.mount_map, filepath=result))

            return mappedResults

        return extractionWrapper
