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
from json import dumps as jsonDumps

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper
from avid.linkers import CaseLinker, FractionLinker

from avid.actions import BatchActionBase
from avid.actions.genericCLIAction import GenericCLIAction
from avid.selectors import TypeSelector
from avid.actions.simpleScheduler import SimpleScheduler
from avid.externals.matchPoint import FORMAT_VALUE_MATCHPOINT

logger = logging.getLogger(__name__)


class MitkMatchImageAction(GenericCLIAction):
    """Class that wraps the single action for the tool MitkMatchImage."""

    @staticmethod
    def _indicate_outputs(actionInstance, **allActionArgs):
        userDefinedProps = {artefactProps.TYPE: artefactProps.TYPE_VALUE_RESULT}

        artefactRef = actionInstance._targetImage[0]
        if actionInstance._targetIsArtefactReference is False:
            if actionInstance._movingImage is None:
                logger.error("Moving image is None and can't be used as Reference")
                raise
            else:
                artefactRef = actionInstance._movingImage[0]

        resultArtefact = actionInstance.generateArtefact(artefactRef,
                                                         userDefinedProps={artefactProps.TYPE:artefactProps.TYPE_VALUE_RESULT,
                                                                           artefactProps.FORMAT: FORMAT_VALUE_MATCHPOINT},
                                                         url_user_defined_part=actionInstance._generateName(),
                                                         url_extension='mapr')
        return [resultArtefact]

    @staticmethod
    def _defaultNameCallable(actionInstance, **allActionArgs):
        name = "reg_"+artefactHelper.getArtefactShortName(actionInstance._movingImage[0])

        if actionInstance._movingMask is not None:
            name += "_" + artefactHelper.getArtefactShortName(actionInstance._movingMask)

        name += "_to_"+artefactHelper.getArtefactShortName(actionInstance._targetImage[0])

        if actionInstance._targetMask is not None:
            name += "_" + artefactHelper.getArtefactShortName(actionInstance._targetMask)

        return name

    def __init__(self, targetImage, movingImage, algorithm, algorithmParameters = None,
                 targetMask=None, target_mask_label=None, movingMask=None, moving_mask_label=None,
                 targetIsArtefactReference=True, actionTag="MitkMatchImage",
                 alwaysDo=False, session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None,
                 generateNameCallable=None, cli_connector=None):
        """
        :param targetImage: Artefact for the target / static image
        :param movingImage: Artefact for the moving image
        :param algorithm: Path to the registration algorithm. This will usually be in the 'bin' folder of your MITK
            and called something like 'mdra-0-14_MITK_MultiModal_rigid_default.dll'
        :param algorithmParameters: Optional arguments that will get passed to the registration via the 'parameters'
            argument (e.g. number of iterations)
        :param targetMask: Optional artefact for a mask for the target image
        :param target_mask_label: Optional label name for the target mask. If the mask is a MultiLabelSegmentation, this
            specifies which label to use. Otherwise, by default the first label will be used
        :param movingMask: Optional artefact for a mask for the moving image
        :param moving_mask_label: Optional label name for the moving mask. If the mask is a MultiLabelSegmentation, this
            specifies which label to use. Otherwise, by default the first label will be used
        :param targetIsArtefactReference: Specifies which artefact the resulting artefact will be based upon, the target
            or the moving image. By default, the registration artefact will be based on the target image.
        """

        self._targetImage = [self._ensureSingleArtefact(targetImage, "targetImage")]
        self._targetMask = [self._ensureSingleArtefact(targetMask, "targetMask")]
        self._movingImage = [self._ensureSingleArtefact(movingImage, "movingImage")]
        self._movingMask = [self._ensureSingleArtefact(movingMask, "movingMask")]
        self._algorithm = algorithm
        self._targetIsArtefactReference = targetIsArtefactReference

        additionalArgs = {'a':self._algorithm}
        if target_mask_label:
            additionalArgs['target_mask_label'] = target_mask_label
        if moving_mask_label:
            additionalArgs['moving_mask_label'] = moving_mask_label

        self._algorithmParameters = algorithmParameters
        if not self._algorithmParameters is None:
            additionalArgs['parameters'] = jsonDumps(self._algorithmParameters).replace('"', '\\"')

        if generateNameCallable is None:
            generateNameCallable = self._defaultNameCallable

        masks = {}
        if self._targetMask:
            masks["target_mask"] = self._targetMask
        if self._movingMask:
            masks["moving_mask"] = self._movingMask

        GenericCLIAction.__init__(self, t=self._targetImage, m=self._movingImage, **masks,
                                  tool_id="MitkMatchImage", outputFlags=['o'],
                                  additionalArgs=additionalArgs, illegalArgs= ['output', 'moving', 'target'],
                                  defaultoutputextension='mapr', actionTag= actionTag, alwaysDo=alwaysDo, session=session,
                                  indicateCallable=self._indicate_outputs, generateNameCallable=generateNameCallable,
                                  additionalActionProps=additionalActionProps,
                                  actionConfig=actionConfig, propInheritanceDict=propInheritanceDict, cli_connector=cli_connector)


class MitkMatchImageBatchAction(BatchActionBase):
    """
    Batch action for MitkMatchImage that performs image registration.

    :param targetSelector: Selector for the target images
    :param movingSelector: Selector for the moving images
    :param movingLinker: Linker to match moving images with their respective target image (default: link by Case)
    :param targetMaskSelector: Optional selector for masks for the target images. If the masks are
        MultiLabelSegmentations, you can specify a label via the argument 'target_mask_label'. Otherwise the first label
        will be used by default
    :param targetMaskLinker: Linker to match target image masks with their respective target image (default: link by
        Case, Case Instance and Time Point)
    :param movingMaskSelector: Optional selector for masks for the moving images. If the masks are
        MultiLabelSegmentations, you can specify a label via the argument 'moving_mask_label'. Otherwise the first label
        will be used by default
    :param movingMaskLinker: Linker to match moving image masks with their respective moving image (default: link by
        Case, Case Instance and Time Point)
    :param algorithm: Path to the registration algorithm to use. This will usually be in the 'bin' folder of your MITK
        and called something like 'mdra-0-14_MITK_MultiModal_rigid_default.dll'
    """

    def __init__(self, targetSelector, movingSelector, movingLinker=None,
                 targetMaskSelector=None, targetMaskLinker=None,
                 movingMaskSelector=None, movingMaskLinker=None,
                 actionTag="MitkMatchImage", session=None,
                 additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):

        additionalInputSelectors = {
            "movingImage": movingSelector,
            "targetMask": targetMaskSelector,
            "movingMask": movingMaskSelector,
        }

        if movingLinker is None:
            movingLinker = CaseLinker()
        linker = {"movingImage": movingLinker}

        if targetMaskSelector:
            if targetMaskLinker is None:
                targetMaskLinker = FractionLinker()
            linker["targetMask"] = targetMaskLinker

        dependent_linker = {}
        if movingMaskSelector:
            if movingMaskLinker is None:
                movingMaskLinker = FractionLinker()
            dependent_linker["movingImage"] = ["movingMask", movingMaskLinker]

        BatchActionBase.__init__(self, actionTag= actionTag, actionClass=MitkMatchImageAction,
                                 primaryInputSelector= targetSelector,
                                 primaryAlias="targetImage", additionalInputSelectors = additionalInputSelectors,
                                 linker=linker, dependentLinker=dependent_linker, session= session,
                                 relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps = additionalActionProps, **singleActionParameters)

