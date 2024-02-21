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

import avid.common.artefact.defaultProps as artefactProps

from . import BatchActionBase
from .genericCLIAction import GenericCLIAction
from avid.selectors import TypeSelector
from .simpleScheduler import SimpleScheduler

logger = logging.getLogger(__name__)

class MitkResampleMaskAction(GenericCLIAction):
    '''Class that wraps the single action for the tool MitkResampleMask.'''

    def __init__(self, images, additionalArgs= None, defaultoutputextension ='nrrd', actionTag="MitkResampleMask",
                 alwaysDo=False, session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None, cli_connector=None):
        GenericCLIAction.__init__(self, i=images, actionID="MitkResampleMask", outputFlags=['o'],
                                  additionalArgs=additionalArgs, illegalArgs= ['output', 'input'], actionTag= actionTag,
                                  alwaysDo=alwaysDo, session=session, additionalActionProps=additionalActionProps,
                                  actionConfig=actionConfig, propInheritanceDict=propInheritanceDict, cli_connector=cli_connector,
                                  defaultoutputextension=defaultoutputextension)


class MitkResampleMaskBatchAction(BatchActionBase):
    '''Batch action for MitkResampleMask.'''

    def __init__(self, imageSelector,
                 actionTag="MitkResampleMask", session=None,
                 additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
        BatchActionBase.__init__(self, actionTag=actionTag, actionClass=MitkResampleMaskAction,
                                 primaryInputSelector=imageSelector,
                                 primaryAlias="images", additionalInputSelectors=None,
                                 linker=None, session=session,
                                 relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps=additionalActionProps,
                                 **singleActionParameters)
