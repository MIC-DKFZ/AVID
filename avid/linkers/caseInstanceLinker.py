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

import avid.common.artefact.defaultProps as artefactProps
from avid.linkers import InnerLinkerBase


class CaseInstanceLinker(InnerLinkerBase):
    """
    Links data on the basis of the artefactProps.CASEINSTANCE entry.
    If strict linkage is false the linker will also accept instances where
    one of primary and secondary is none and the other has a defined value.
    """

    def __init__(
        self,
        useStrictLinkage=False,
        allowOnlyFullLinkage=True,
        performInternalLinkage=False,
    ):
        """@param useStrictLinkage If true it will only link with the very same instance id.
        If false, it will treat None as wildcard that also matches."""
        InnerLinkerBase.__init__(
            self,
            allowOnlyFullLinkage=allowOnlyFullLinkage,
            performInternalLinkage=performInternalLinkage,
        )

        self._useStrictLinkage = useStrictLinkage

    def _findLinkedArtefactOptions(self, primaryArtefact, secondarySelection):
        linkValue = None

        if (
            primaryArtefact is not None
            and artefactProps.CASEINSTANCE in primaryArtefact
        ):
            linkValue = primaryArtefact[artefactProps.CASEINSTANCE]

        result = list()
        for secondArtefact in secondarySelection:
            if (
                secondArtefact is not None
                and artefactProps.CASEINSTANCE in secondArtefact
            ):
                itemValue = secondArtefact[artefactProps.CASEINSTANCE]
                if itemValue == linkValue or (
                    not self._useStrictLinkage
                    and (linkValue is None or itemValue is None)
                ):
                    result.append(secondArtefact)
            else:
                if linkValue is None:
                    # key does not exist, but selection value is None, therefore it is a match
                    result.append(secondArtefact)

        return result
