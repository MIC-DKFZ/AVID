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

import avid.common.artefact as artefactHelper
import avid.common.artefact.defaultProps as artefactProps
from avid.common import AVIDUrlLocater
from avid.common.cliConnector import DefaultCLIConnector

from . import SingleActionBase

logger = logging.getLogger(__name__)


class CLIActionBase(SingleActionBase):
    """Base action for all actions that have the following pattern:
    They prepare the execution of an command line (e.g. by generating the needed
    batch file(s) or input data) and then the command line will be executed. This
    is standardized by this class. Derived classes just need to implement
    _indicateOutputs() and _prepareCLIExecution(). The rest is done by the base class.
    In _prepareCLIExecution() everything should be prepared/generated that is needed
    for the CLI call to run properly. Then the call should be returned as result of
    the method."""

    def __init__(
        self,
        actionTag,
        alwaysDo=False,
        session=None,
        additionalActionProps=None,
        cwd=None,
        tool_id=None,
        actionConfig=None,
        propInheritanceDict=None,
        cli_connector=None,
    ):
        """@param cwd Specifies the current working directory that should be used for the cli call.
        if not set explicitly, it will be deduced automatically by the specified tool/action
        """
        SingleActionBase.__init__(
            self,
            actionTag=actionTag,
            alwaysDo=alwaysDo,
            session=session,
            additionalActionProps=additionalActionProps,
            propInheritanceDict=propInheritanceDict,
        )
        self._actionID = tool_id
        self._actionConfig = actionConfig
        self._cwd = cwd
        if self._cwd is None and self._actionID is not None:
            self._cwd = os.path.dirname(
                AVIDUrlLocater.get_tool_executable_url(
                    self._session, tool_id, actionConfig
                )
            )

        self._last_log_file_path = None
        self._last_log_error_file_path = None

        self._cli_connector = cli_connector
        if self._cli_connector is None:
            self._cli_connector = DefaultCLIConnector()

        self._last_call_content = None
        self._last_cli_call = None

    @property
    def cwd(self):
        """returns the current working directory that is used by the action when executing the tool."""
        return self._cwd

    @property
    def logFilePath(self):
        """Returns the path of the log file that contains the std::out stream of the execution, the action instance
        is associated with. If it is None the action was not executed so far."""
        return self._last_log_file_path

    @property
    def logErrorFilePath(self):
        """Returns the path of the error log file that contains the std::error stream of the execution, the action
        instance is associated with. If it is None the action was not executed so far.
        """
        return self._last_log_error_file_path

    @property
    def last_cli_call_file_path(self):
        return self._last_cli_call

    def _prepareCLIExecution(self):
        """Internal function that should prepare/generate everything that is needed
        for the CLI call to run properly (e.g. the batch/bash file that should be
        executed. It is called in the do_setup stage if the base implementation of
        _do_setup indicates the need of processing.
         @return The returnvalue is a string/stream containing all the instructions that
          should be executed in the command line. The CLIActionBase will store it into a shell script and
          execute it."""
        raise NotImplementedError(
            "Reimplement in a derived class to function correctly."
        )
        # Implement: generation of all needed artefact and preperation of the cli call
        pass

    def _postProcessCLIExecution(self):
        """Internal function that should postprocess everything that is needed
        after the CLI call to leave the action and its result in a proper state.
        It is called at the beginning of the do_finalize stage."""
        # Implement: if something should be done after the execution, do it here
        pass

    def _do_setup(self):
        processing_needed = SingleActionBase._do_setup(self)

        if processing_needed:
            self._last_call_content = self._prepareCLIExecution()

            # by policy the first artefact always determines the location and such.
            cliArtefact = self.generateArtefact(
                self.outputArtefacts[0],
                userDefinedProps={
                    artefactProps.TYPE: artefactProps.TYPE_VALUE_MISC,
                    artefactProps.FORMAT: artefactProps.FORMAT_VALUE_BAT,
                },
            )

            path = artefactHelper.generateArtefactPath(self._session, cliArtefact)
            cliName = os.path.join(
                path,
                os.path.split(
                    artefactHelper.getArtefactProperty(
                        self.outputArtefacts[0], artefactProps.URL
                    )
                )[1],
            )

            self._last_cli_call = self._cli_connector.generate_cli_file(
                cliName, self._last_call_content
            )

            self._last_log_file_path = self._last_cli_call + os.extsep + "log"
            self._last_log_error_file_path = (
                self._last_cli_call + os.extsep + "error.log"
            )

        return processing_needed

    def _do_finalize(self):

        self._postProcessCLIExecution()

        return SingleActionBase._do_finalize(self)

    def _generateOutputs(self):
        self._cli_connector.execute(
            self._last_cli_call,
            log_file_path=self._last_log_file_path,
            error_log_file_path=self._last_log_error_file_path,
            cwd=self._cwd,
        )
