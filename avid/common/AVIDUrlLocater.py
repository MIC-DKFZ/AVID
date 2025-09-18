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

from pathlib import Path
import os
import logging
import avid.common.config_mangager as cfg


logger = logging.getLogger(__name__)


def get_avid_project_root_path():
    '''
    identifies the root dir of the AVID project source dir
    '''
    # get the location of this file (to be precisely it's the .pyc)
    path = os.path.dirname(__file__)

    # navigate to the root dir - to do so we navigate the directory tree upwards
    return Path(os.path.split(os.path.split(path)[0])[0])


def ensure_existance(func):
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)
        if result.exists():
            return result
        else:
            raise Exception("Tried to get path {} that does not exist.".format(result))

    return inner


@ensure_existance
def get_tool_package_config_dir(package):
    return get_avid_project_root_path() / "tool-packages" / package


@ensure_existance
def get_tool_package_source_config_path(package):
    return get_tool_package_config_dir(package) / "sources.config"


@ensure_existance
def get_tool_package_tools_config_path(package):
    return get_tool_package_config_dir(package) / "tools.config"


def get_tool_config_dir(actionID, workflowRootPath=None, checkExistance=True):
    """
    Helper functions that gets the path to the config dir for the passed actionID
    If workflowRootPath is set it will be also checked
    :param actionID: actionID of the action that requests the URL
    :param workflowRootPath: Path of the workflow. If none it will be ignored.
    :param checkExistance: Indicates if only existing paths should be returned. If True and config path
    does not exist or can be determined, None will be returned.

    The following rules will be used to determine the tool config path.
    1. check the path workflowRootPath/tools/<actionID>. If it is valid, return it, else 2.
    2. check get_venv_tool_config_file_path. If it is valid, return it, else 3.
    2. check get_user_tool_config_file_path. If it is valid, return it, else 4.
    4. return None
    """

    tool_dir = (Path(workflowRootPath) / "tools" / actionID) if workflowRootPath else None
    if not tool_dir or not tool_dir.exists():
        tool_dir = cfg.get_venv_tool_config_dir(tool_id=actionID)
    if not tool_dir.exists():
        tool_dir = cfg.get_user_tool_config_dir(tool_id=actionID)

    if tool_dir.exists() or not checkExistance:
        return tool_dir

    return None

def getToolConfigPath(actionID, workflowRootPath=None, checkExistance=True):
    """
    Helper functions that gets the path to the config file for the passed actionID
    If workflowRootPath is set it will be also checked
    :param actionID: actionID of the action that requests the URL
    :param workflowRootPath: Path of the workflow. If none it will be ignored.
    :param checkExistance: Indicates if only existing paths should be returned. If True and config path
    does not exist or can be determined, None will be returned.

    The following rules will be used to determine the tool config path.
    1. check the path workflowRootPath/tools/<actionID>/avidtool.config. If it is valid, return it, else 2.
    2. check get_venv_tool_config_file_path. If it is valid, return it, else 3.
    2. check get_user_tool_config_file_path. If it is valid, return it, else 4.
    4. return None
    """

    config_path = (Path(workflowRootPath) / "tools" / actionID / cfg.TOOL_CONFIG_FILENAME) if workflowRootPath else None
    if not config_path or not config_path.is_file():
        config_path = cfg.get_venv_tool_config_file_path(tool_id=actionID)
    if not config_path.is_file():
        config_path = cfg.get_user_tool_config_file_path(tool_id=actionID)

    if config_path.is_file() or not checkExistance:
        return config_path

    return None


def getExecutableURL(workflow, actionID, actionConfig=None):
    """
       returns url+executable for a actionID request
       @param actionID of the action that requests the URL
       @param actionConfig specifies if a certian configuration of an action should be used.
       1. checks if there is a valid tool in workflow.actionTools[actionID]. If there is, return it else 2.
       2. check the path:workflowRootPath/tools/<actionID>/avidtool.config. If it is valid, return it else 3.
       3. check the path:<AVID toolspath>/<actionID>/avidtool.config. If it is valid, return it else 4.
       4. check path:avidRoot/Utilities/<defaultRelativePath>. If it is valid, return it else 5.
       5. return None
    """
    returnURL = None

    try:
        if actionID in workflow.actionTools:
            # option 1
            returnURL = workflow.actionTools[actionID]
    except:
        pass

    if returnURL is None:
        # option 2-4
        workflowRootPath = workflow.rootPath if workflow else None
        toolconfigPath = getToolConfigPath(actionID, workflowRootPath)

        if toolconfigPath and os.path.isfile(str(toolconfigPath)):
            config = cfg._load_toml(toolconfigPath)

            if not actionConfig:
                actionConfig = 'default'
            execURL = cfg.get_setting_from_dict(key=f"{actionConfig}.exe", config_dict=config)

            if not os.path.isabs(execURL):
                execURL = os.path.join(os.path.dirname(toolconfigPath), execURL)

            if os.path.isfile(execURL):
                returnURL = execURL
            else:
                logger.error(
                    'ExecURL for action "%s" is invalid. ToolConfigPath: "%s"; ExecURL: "%s".',
                    actionID, toolconfigPath, execURL)
        else:
            logger.error(
                'ToolConfigPath for action "%s" is invalid. ToolConfigPath "%s".',
                actionID, toolconfigPath)

    if returnURL is None:
        logger.error(
            'Action "%s" seems not to have a configured tool. Please use avidconfig and see the README.md for information how to do it.',
            actionID)
    elif not os.path.exists(returnURL):
        logger.debug('Found executable URL for action "%s" seems to be invalid. Found URL: %s', actionID, returnURL)

    return returnURL
