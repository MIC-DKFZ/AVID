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
import shutil
import stat
import sys
from builtins import str
from os import listdir
from os.path import isfile, join

import avid.common.artefact as artefactHelper
import avid.common.artefact.defaultProps as artefactProps

from . import ActionBase, BatchActionBase
from .simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)


class cleanWorkflowAction(ActionBase):
    """Removes the passed selection from the workflow and also deletes the referenced files"""

    def __init__(
        self,
        deleteArtefact,
        deleteWholeDirectory=False,
        removeWriteProtection=False,
        actionTag="clean",
        session=None,
        additionalActionProps=None,
    ):
        ActionBase.__init__(self, actionTag, session, additionalActionProps)

        self._deleteArtefact = deleteArtefact
        self._deleteWholeDirectory = deleteWholeDirectory
        self._removeWriteProtection = removeWriteProtection

    def _generateName(self):
        name = "Clean_" + str(
            artefactHelper.getArtefactProperty(
                self._deleteArtefact, artefactProps.ACTIONTAG
            )
        )
        return name

    def _indicateOutputs(self):
        return list()

    def _do(self):
        """Removes the passed selection from the workflow and also deletes the referenced files"""
        try:
            delURL = artefactHelper.getArtefactProperty(
                self._deleteArtefact, artefactProps.URL
            )
            if delURL:
                if self._deleteWholeDirectory:
                    dirToDelete = os.path.dirname(os.path.abspath(delURL))
                    if os.path.exists(dirToDelete):
                        if self._removeWriteProtection:
                            files = self._getListOfFiles(dirToDelete)
                            self._removeWriteProtection(dirToDelete, files)
                        shutil.rmtree(dirToDelete)
                else:
                    self._session.artefacts.remove(self._deleteArtefact)
                    os.remove(delURL)
            else:
                logger.info("nothing deleted!")

        except:
            logger.error("Unexpected error: %s", sys.exc_info()[0])
            raise

        return (ActionBase.ACTION_SUCCESS, list())

    def _getListOfFiles(self, directory):
        allFiles = [f for f in listdir(directory) if isfile(join(directory, f))]
        return allFiles

    def _removeWriteProtection(self, directory, files):
        for aFile in files:
            fileWithDirectory = os.path.join(directory, aFile)
            os.chmod(fileWithDirectory, stat.S_IWRITE)


class cleanWorkflowBatchAction(BatchActionBase):
    """Batch action work the cleaning of the workflow."""

    def __init__(
        self,
        deleteSelector,
        deleteWholeDirectory=False,
        removeWriteProtection=False,
        actionTag="clean",
        session=None,
        additionalActionProps=None,
        scheduler=SimpleScheduler(),
    ):
        BatchActionBase.__init__(
            self, actionTag, True, scheduler, session, additionalActionProps
        )

        self._deleteArtefacts = deleteSelector.getSelection(self._session.artefacts)

        self._deleteWholeDirectory = deleteWholeDirectory
        self._removeWriteProtection = removeWriteProtection

    def _generateActions(self):
        # filter only type result. Other artefact types are not interesting

        actions = list()

        for artefact in self._deleteArtefacts:
            action = cleanWorkflowAction(
                artefact,
                self._deleteWholeDirectory,
                self._removeWriteProtection,
                self._actionTag,
                session=self._session,
                additionalActionProps=self._additionalActionProps,
            )
            actions.append(action)

        return actions
