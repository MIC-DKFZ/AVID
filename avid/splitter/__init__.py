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

from builtins import object


class BaseSplitter(object):
    '''base clase for functors used to split a artefact list by certain criterias
    and pass back a list of splitted artefact lists.
    The default implementation does not touch the selection at all and just passes back a copy of the passed selection
    as first (and only) split list element.'''

    def __init__(self):
        pass

    def splitSelection(self, selection):
        '''
        does nothing
        '''
        return [selection.copy()]


from .keyValueSplitter import KeyValueSplitter
from .keyValueSplitter import CaseSplitter
from .keyValueSplitter import FractionSplitter
from .singleSplitter import SingleSplitter
