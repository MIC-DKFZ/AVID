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

from .__init__ import LinkerBase


class PosLinker(LinkerBase):
    """Links only by position. Therefore selection is secondarySelection[primaryIndex].
    If primaryIndex is larger then len(secondarySelection) it will be the last element
    of the slave selection.
    """

    def __init__(self):
        LinkerBase.__init__(self, allowOnlyFullLinkage=False)

    def _getLinkedSelection(self, primaryIndex, primarySelections, secondarySelections):
        index = primaryIndex
        if index > len(secondarySelections):
            index = len(secondarySelections) - 1

        resultSelections = list(
            list(),
        )

        if index >= 0:
            resultSelections.append(secondarySelections[index])

        return resultSelections
