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
from pathlib import Path

import avid.common.artefact.defaultProps as artefactProps

from . import BatchActionBase
from .genericCLIAction import GenericCLIAction
from avid.selectors import TypeSelector
from .simpleScheduler import SimpleScheduler
from ..common.artefact import getArtefactProperty

logger = logging.getLogger(__name__)

def collectSplitOutputs(actionInstance, indicatedOutputs, i, artefactHelper=None, **allArgs):
    outputs = indicatedOutputs.copy()

    temp_output = indicatedOutputs[0]

    file_url = getArtefactProperty(temp_output, artefactProps.URL)

    if not os.path.isfile(file_url):
        # if indicated output does not exists, the input was splitted.
        multi_volume_outputs = list()

        file_path = Path(file_url)
        file_full_extension = ''.join(file_path.suffixes)
        file_stem = file_url[:-len(file_full_extension)]

        search_pattern = file_stem+'_*'+file_full_extension

        find_files = glob(search_pattern)

        for new_file in find_files:
            # Search for the time step in the file path
            new_file_stem = new_file[:-len(file_full_extension)]
            timestep_str = new_file_stem[new_file_stem.rfind('_')+1:]

            new_artefact = temp_output.clone()
            new_artefact[artefactProps.RESULT_SUB_TAG] = timestep_str
            new_artefact[artefactProps.URL] = new_file
            new_artefact[MitkSplit4Dto3DImagesAction.PROPERTY_DYNAMIC_SOURCE] = i[0][artefactProps.ID]
            new_artefact[MitkSplit4Dto3DImagesAction.PROPERTY_ORIGINAL_TIME_STEP] = timestep_str
            multi_volume_outputs.append(new_artefact)

        if len(multi_volume_outputs) > 0:
            # only replace outputs if we realy have found something
            outputs = multi_volume_outputs

    return outputs

class MitkSplit4Dto3DImagesAction(GenericCLIAction):
    '''Class that wraps the single action for the tool MitkSplit4Dto3DImages.'''

    '''In case actions produce more then one result artefact, this property may be used to make the results distinguishable.'''
    PROPERTY_DYNAMIC_SOURCE = "MitkSplit4Dto3DImagesAction_dynamic_source"
    PROPERTY_ORIGINAL_TIME_STEP = "MitkSplit4Dto3DImagesAction_original_time_step"

    def __init__(self, inputs, readerName= None, defaultoutputextension ='nrrd', actionTag="MitkSplit4Dto3DImages",
                 alwaysDo=False, session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None, cli_connector=None):
        addArgs = None
        if readerName is not None:
            addArgs = {'r':readerName}

        GenericCLIAction.__init__(self, i=inputs, actionID="MitkSplit4Dto3DImages", outputFlags=['o'],
                                  additionalArgs=addArgs, illegalArgs= ['output', 'input'], actionTag= actionTag,
                                  alwaysDo=alwaysDo, session=session, additionalActionProps=additionalActionProps,
                                  actionConfig=actionConfig, propInheritanceDict=propInheritanceDict, cli_connector=cli_connector,
                                  defaultoutputextension=defaultoutputextension,
                                  collectOutputsCallable=collectSplitOutputs)


class MitkSplit4Dto3DImagesBatchAction(BatchActionBase):
    '''Batch action for MitkSplit4Dto3DImages.'''

    def __init__(self, inputSelector,
                 actionTag="MitkSplit4Dto3DImages", session=None,
                 additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
        BatchActionBase.__init__(self, actionTag=actionTag, actionClass=MitkSplit4Dto3DImagesAction,
                                 primaryInputSelector=inputSelector,
                                 primaryAlias="inputs", additionalInputSelectors=None,
                                 linker=None, session=session,
                                 relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps=additionalActionProps,
                                 **singleActionParameters)
