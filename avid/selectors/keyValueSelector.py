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

import avid.common.artefact.defaultProps as artefactProps
from avid.common.artefact import ArtefactCollection
from avid.selectors import SelectorBase


class KeyValueSelector(SelectorBase):
    """
    extracts the entries of the working data, which has the specified key//value entries.
    e.g.
    key = "tag", value = "CCT"
    the selectors extracts all rows, which have a key tag, and the value is CCT.
    """

    def __init__(
        self,
        key,
        value,
        negate=False,
        allowStringCompare=False,
        allowNoneEquality=False,
    ):
        """init"""
        super().__init__()
        self.__key = key
        self.__value = value
        self.__allowStringCompare = allowStringCompare
        self.__allowNoneEquality = allowNoneEquality
        self.__negate = negate

    def getSelection(self, workflowData):
        """Filters the given collection of entries and returns all selected entries"""
        outCollection = ArtefactCollection()

        for entry in workflowData:
            if self.__key in entry:
                if self.__allowStringCompare:
                    validValue = (
                        entry[self.__key] is not None
                        and self.__value is not None
                        and str(entry[self.__key]) == str(self.__value)
                    )

                    if (not self.__negate and validValue) or (
                        self.__negate and not validValue
                    ):
                        outCollection.add_artefact(entry)
                else:
                    equalValue = entry[self.__key] == self.__value
                    if (
                        not equalValue
                        and self.__allowNoneEquality
                        and self.__value is None
                    ):
                        equalValue = entry[self.__key] is None
                    if (not self.__negate and equalValue) or (
                        self.__negate and not equalValue
                    ):
                        outCollection.add_artefact(entry)
            else:
                if self.__value is None:
                    # key does not exist, but selection value is None, therefore it is a match
                    outCollection.add_artefact(entry)
        return outCollection


class ActionTagSelector(KeyValueSelector):
    """Convenience selector to select by a special action tag value."""

    def __init__(self, tagValue, negate=False):
        """init"""
        KeyValueSelector.__init__(self, artefactProps.ACTIONTAG, tagValue, negate)


class CaseSelector(KeyValueSelector):
    """Convenience selector to select by the case id."""

    def __init__(self, keyValue, negate=False):
        """init"""
        KeyValueSelector.__init__(self, artefactProps.CASE, keyValue, negate)


class CaseInstanceSelector(KeyValueSelector):
    """Convenience selector to select by the case instance id."""

    def __init__(self, keyValue, negate=False):
        """init"""
        KeyValueSelector.__init__(
            self, artefactProps.CASEINSTANCE, keyValue, negate, True
        )


class TimepointSelector(KeyValueSelector):
    """Convenience selector to select by the timepoint."""

    def __init__(self, keyValue, negate=False):
        """init"""
        KeyValueSelector.__init__(self, artefactProps.TIMEPOINT, keyValue, negate)


class TypeSelector(KeyValueSelector):
    """Convenience selector to select by the type."""

    def __init__(self, keyValue, negate=False):
        """init"""
        KeyValueSelector.__init__(self, artefactProps.TYPE, keyValue, negate, True)


class ResultSelector(TypeSelector):
    """Convenience selector to select all artefacts of type result."""

    def __init__(self, negate=False):
        """init"""
        TypeSelector.__init__(self, artefactProps.TYPE_VALUE_RESULT, negate)


class FormatSelector(KeyValueSelector):
    """Convenience selector to select by the format of the artefact file."""

    def __init__(self, keyValue, negate=False):
        """init"""
        KeyValueSelector.__init__(self, artefactProps.FORMAT, keyValue, negate, True)


class ObjectiveSelector(KeyValueSelector):
    """Convenience selector to select by the objective of the artefact file."""

    def __init__(self, keyValue, negate=False):
        """init"""
        KeyValueSelector.__init__(self, artefactProps.OBJECTIVE, keyValue, negate, True)


class DoseStatSelector(KeyValueSelector):
    """Convenience selector to select by the dose stat of the artefact file."""

    def __init__(self, keyValue, negate=False):
        """init"""
        KeyValueSelector.__init__(self, artefactProps.DOSE_STAT, keyValue, negate, True)
