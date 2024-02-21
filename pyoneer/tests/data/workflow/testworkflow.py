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

from builtins import str
import sys
import argparse

import avid.common.workflow as workflow
from avid.common.artefact import defaultProps, addArtefactToWorkflowData
from avid.common.artefact import generateArtefactEntry

from avid.selectors import ActionTagSelector

#this is a test workflow that allow basic testing of pyoneer functionalities: evaluation and optimization.
#The workflow is not a real fully fletched avid workflow.
#It does the following:
# - take every artefact with action tag "input" gets the property "myValue"
# - computes a new value given |10-x|*myValue
# - generate a result artefact for every input and stores the according new value as the Property "myValue"
#
#It takes to command line modifier:
#--delay: defines the value ot the execution_duration property of the result artefacts
#--x: Part of the described function above.
#This workflow allows to simulate duration changes and result changes due to deferent workflow settings.

if __name__ == "__main__":
    __this__ = sys.modules[__name__]

    parser = argparse.ArgumentParser()
    parser.add_argument('--delay', type=float)
    parser.add_argument('--x', type=float)
    cliargs, unknown = parser.parse_known_args()

    delay = 0
    if cliargs.delay is not None:
      delay = abs(cliargs.delay)

    x = 0
    if cliargs.x is not None:
      x = cliargs.x

    with workflow.initSession_byCLIargs(expandPaths = True, autoSave = True) as session:
      inputs = ActionTagSelector("Input").getSelection(session.artefacts)

      for input in inputs:
          myValue = float(input['myValue'])
          newValue = abs(10-x/10)*myValue
          newArtefact = generateArtefactEntry(input[defaultProps.CASE], input[defaultProps.CASEINSTANCE],
                                              input[defaultProps.TIMEPOINT], "Result", defaultProps.TYPE_VALUE_RESULT,
                                              input[defaultProps.FORMAT], url=input[defaultProps.URL], myValue = str(newValue))
          newArtefact[defaultProps.EXECUTION_DURATION] = str(delay)

          addArtefactToWorkflowData(session.artefacts, newArtefact)
