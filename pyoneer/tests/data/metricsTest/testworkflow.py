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

import sys
import os
import argparse

import avid.common.workflow as workflow

from avid.selectors import ActionTagSelector
from avid.actions.mapR import mapRBatchAction as mapR

if __name__ == "__main__":
    __this__ = sys.modules[__name__]

    parser = argparse.ArgumentParser()
    parser.add_argument('--modifier1', type=int)
    cliargs, unknown = parser.parse_known_args()

    actionProps = None

    if cliargs.modifier1 is not None:
        actionProps = {'modifier1': cliargs.modifier1}

    with workflow.initSession_byCLIargs(expandPaths = True, autoSave = True) as session:
      mapR(ActionTagSelector("Moving"), registrationSelector = ActionTagSelector("Registration"), templateSelector=ActionTagSelector("Target"), actionTag = "Result", additionalActionProps= actionProps).do()