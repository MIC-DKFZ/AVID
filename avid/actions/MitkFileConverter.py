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
from copy import copy
from glob import glob

import avid.common.artefact.defaultProps as artefactProps

from . import BatchActionBase
from .genericCLIAction import GenericCLIAction
from avid.selectors import TypeSelector
from .simpleScheduler import SimpleScheduler
from ..common.artefact import getArtefactProperty

logger = logging.getLogger(__name__)

def collectFileConverterOutputs(actionInstance, indicatedOutputs, artefactHelper=None, **allArgs):
    outputs = list()

    temp_output = indicatedOutputs[0]

    file_path = getArtefactProperty(temp_output, artefactProps.URL)

    if os.path.isfile(file_path):
        # if indicated output exists, there is nothing to do.
        outputs = indicatedOutputs.copy()
    else:
        file_name, file_extension = os.path.splitext(file_path)

        search_pattern = file_name+'_*'+file_extension

        find_files = glob(search_pattern)

        result_sub_tag = 0
        for file in find_files:
            new_artefact = copy(temp_output)
            new_artefact[artefactProps.RESULT_SUB_TAG] = result_sub_tag
            new_artefact[artefactProps.URL] = file
            result_sub_tag += 1
            outputs.append(new_artefact)

    return outputs

class MitkFileConverterAction(GenericCLIAction):
    '''Class that wraps the single action for the tool MitkFileConverter.'''

    def __init__(self, inputs, readerName= None, defaultoutputextension ='nrrd', actionTag="MitkFileConverter",
                 alwaysDo=False, session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None, cli_connector=None):
        addArgs = None
        if readerName is not None:
            addArgs = {'r':readerName}

        GenericCLIAction.__init__(self, i=inputs, actionID="MitkFileConverter", outputFlags=['o'],
                                  additionalArgs=addArgs, illegalArgs= ['output', 'input'], actionTag= actionTag,
                                  alwaysDo=alwaysDo, session=session, additionalActionProps=additionalActionProps,
                                  actionConfig=actionConfig, propInheritanceDict=propInheritanceDict, cli_connector=cli_connector,
                                  defaultoutputextension=defaultoutputextension,
                                  collectOutputsCallable=collectFileConverterOutputs)


class MitkFileConverterBatchAction(BatchActionBase):
    '''Batch action for MitkFileConverter.'''

    def __init__(self, inputSelector,
                 actionTag="MitkFileConverter", session=None,
                 additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
        BatchActionBase.__init__(self, actionTag=actionTag, actionClass=MitkFileConverterAction,
                                 primaryInputSelector=inputSelector,
                                 primaryAlias="inputs", additionalInputSelectors=None,
                                 linker=None, session=session,
                                 relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps=additionalActionProps,
                                 **singleActionParameters)
