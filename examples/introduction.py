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

###############################################################################
# Imports
###############################################################################
import os
import avid.common.workflow as workflow

from avid.actions.pythonAction import PythonUnaryBatchAction, PythonBinaryBatchAction
from avid.selectors import ActionTagSelector, CaseSelector, ValiditySelector
from avid.linkers import CaseLinker, TimePointLinker

###############################################################################
# Initialize session with existing Artefacts
###############################################################################
session =  workflow.initSession(bootstrapArtefacts=os.path.join(os.getcwd(),'output', 'bootstrap.avid'),
                                sessionPath=os.path.join(os.getcwd(),'output', 'example.avid'),
                                expandPaths=True,
                                debug=True,
                                autoSave = True)


def write_filename(outputs, inputs, **kwargs):
    """
        Simple callable that outputs a sentence including the filename of the input
    """
    inputName = inputs[0]

    with open(outputs[0], "w") as ofile:
        ofile.write(f"Result for file is '{inputName}'")


allValid_selector = ValiditySelector()

with session:
    PythonUnaryBatchAction(
        inputSelector=allValid_selector,
        generateCallable=write_filename,
        actionTag="example1",
        defaultoutputextension="txt"
    )

    session.run_batches()
