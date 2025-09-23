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

"""
Locate AVID configuration, workflow, and tool paths.

   used to identify the location of a action specific tool.

   every action has to use this action tool location routines!
"""

import logging
import os
from pathlib import Path

import avid.common.config_manager as cfg

logger = logging.getLogger(__name__)


def get_avid_package_root_dir():
    """
    identifies the root dir of the AVID package
    """
    # get the location of this file (to be precisely it's the .pyc)
    path = os.path.dirname(__file__)

    # navigate to the root dir - to do so we navigate the directory tree upwards
    return Path(os.path.split(path)[0])


def ensure_existence(func):
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)
        if result.exists():
            return result
        else:
            raise Exception("Tried to get path {} that does not exist.".format(result))

    return inner


@ensure_existence
def get_tool_package_config_dir(package):
    return get_avid_package_root_dir() / "cli" / "tool-packages" / package


@ensure_existence
def get_tool_package_source_config_path(package):
    return get_tool_package_config_dir(package) / "sources.config"


@ensure_existence
def get_tool_package_tools_config_path(package):
    return get_tool_package_config_dir(package) / "tools.config"


def get_tool_config_dir(tool_id, workflow_root_path=None, check_existence=True):
    """
    Helper functions that gets the path to the config dir for the passed tool_id
    If workflowRootPath is set it will be also checked
    :param tool_id: tool_id of the action that requests the URL
    :param workflow_root_path: Path of the workflow. If none it will be ignored.
    :param check_existence: Indicates if only existing paths should be returned. If True and config path
    does not exist or can't be determined, None will be returned.

    The following rules will be used to determine the tool config path.
    1. check the path workflowRootPath/tools/<tool_id>. If it is valid, return it, else 2.
    2. check get_venv_tool_config_file_path. If it is valid, return it, else 3.
    3. check get_user_tool_config_file_path. If it is valid, return it, else 4.
    4. return None
    """

    tool_dir = (
        (Path(workflow_root_path) / "tools" / tool_id) if workflow_root_path else None
    )
    if not tool_dir or not tool_dir.exists():
        tool_dir = cfg.get_venv_tool_config_dir(tool_id=tool_id)
    if not tool_dir or not tool_dir.exists():
        tool_dir = cfg.get_user_tool_config_dir(tool_id=tool_id)

    if tool_dir.exists() or not check_existence:
        return tool_dir

    return None


def get_tool_config_file_path(tool_id, workflow_root_path=None, check_existence=True):
    """
    Helper function that gets the path to the config file for the passed tool_id
    If workflow_root_path is set it will be also checked
    :param tool_id: tool_id of the action that requests the URL
    :param workflow_root_path: Path of the workflow. If none it will be ignored.
    :param check_existence: Indicates if only existing paths should be returned. If True and config path
    does not exist or can't be determined, None will be returned.

    The following rules will be used to determine the tool config path.
    1. check the path workflowRootPath/tools/<tool_id>/avidtool.config. If it is valid, return it, else 2.
    2. check get_venv_tool_config_file_path. If it is valid, return it, else 3.
    3. check get_user_tool_config_file_path. If it is valid, return it, else 4.
    4. return None
    """

    config_path = (
        (Path(workflow_root_path) / "tools" / tool_id / cfg.TOOL_CONFIG_FILENAME)
        if workflow_root_path
        else None
    )
    if not config_path or not config_path.is_file():
        config_path = cfg.get_venv_tool_config_file_path(tool_id=tool_id)
    if not config_path or not config_path.is_file():
        config_path = cfg.get_user_tool_config_file_path(tool_id=tool_id)

    if config_path.is_file() or not check_existence:
        return config_path

    return None


def get_tool_executable_url(workflow, tool_id, action_config=None):
    """
    returns url+executable for a tool id request
    @param tool_id of the action/tool for which the URL is requested
    @param action_config specifies if a certain configuration of an action should be used.
    1. checks if there is a valid tool in workflow.actionTools[tool_id]. If there is, return it else 2.
    2. check the path:workflowRootPath/tools/<tool_id>/avidtool.config. If it is valid, return it else 3.
    3. check the path:<AVID toolspath>/<tool_id>/avidtool.config. If it is valid, return it else 4.
    4. check path:avidRoot/Utilities/<defaultRelativePath>. If it is valid, return it else 5.
    5. return None
    """
    returnURL = None

    try:
        if tool_id in workflow.actionTools:
            # option 1
            returnURL = workflow.actionTools[tool_id]
    except:
        pass

    if returnURL is None:
        # option 2-4
        workflowRootPath = workflow.rootPath if workflow else None
        toolconfigPath = get_tool_config_file_path(tool_id, workflowRootPath)

        if toolconfigPath and os.path.isfile(str(toolconfigPath)):
            config = cfg._load_toml(toolconfigPath)

            if not action_config:
                action_config = "default"
            execURL = cfg.get_setting_from_dict(
                key=f"{action_config}.exe", config_dict=config
            )

            if not os.path.isabs(execURL):
                execURL = os.path.join(os.path.dirname(toolconfigPath), execURL)

            if os.path.isfile(execURL):
                returnURL = execURL
            else:
                logger.error(
                    'ExecURL for action "%s" is invalid. ToolConfigPath: "%s"; ExecURL: "%s".',
                    tool_id,
                    toolconfigPath,
                    execURL,
                )
        else:
            logger.error(
                'ToolConfigPath for action "%s" is invalid. ToolConfigPath "%s".',
                tool_id,
                toolconfigPath,
            )

    if returnURL is None:
        logger.error(
            'Action "%s" seems not to have a configured tool. Please use avidconfig and see the README.md for information how to do it.',
            tool_id,
        )
    elif not os.path.exists(returnURL):
        logger.debug(
            'Found executable URL for action "%s" seems to be invalid. Found URL: %s',
            tool_id,
            returnURL,
        )

    return returnURL
