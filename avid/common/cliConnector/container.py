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
import stat

from avid.common import osChecker
from avid.common.cliConnector import (URLMappingCLIConnectorBase,
                                      default_artefact_url_extraction_delegate)

logger = logging.getLogger(__name__)


class ContainerCLIConnectorBase(URLMappingCLIConnectorBase):
    """Base Implementation that allows to execute an action in a container."""

    def __init__(self, mount_map):
        """
        :param mount_map: Dictionary that contains the mapping between relevant paths
            outside of the container (those stored in the session) and the pathes that will
            be known in the container. Needed to properly convert artefact urls.
            Key of the map is the mount path inside of the container, the value is the respective
            path outside.
        """
        super().__init__(mount_map)
        pass

    def generate_cli_file(self, file_path_base, content):
        """Function generates the CLI file based on the passed file name base (w/o extension, extension will be added)
         and the content. It returns the full path to the CLI file."""

        file_name = file_path_base + os.extsep + 'sh'

        path = os.path.split(file_name)[0]

        try:
            content = 'Xvfb :99 -screen 0 1024x768x24 &\n export DISPLAY=:99\n exec "$@"' + '\n' + content
            osChecker.checkAndCreateDir(path)
            with open(file_name, "w") as outputFile:
                if not osChecker.isWindows():
                    content = '#!/bin/bash' + '\n' + content
                outputFile.write(content)
                outputFile.close()

            if not osChecker.isWindows():
                st = os.stat(file_name)
                os.chmod(file_name, st.st_mode | stat.S_IXUSR)

        except Exception:
            raise

        return file_name

    def execute(self, cli_file_path, log_file_path=None, error_log_file_path=None, cwd=None):
        raise NotImplementedError
