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

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper
from avid.common.osChecker import checkAndCreateDir

from avid.actions import BatchActionBase
from avid.actions import SingleActionBase
from avid.linkers import CaseLinker, CaseInstanceLinker
from avid.selectors import TypeSelector
from avid.actions.simpleScheduler import SimpleScheduler
from avid.splitter import KeyValueSplitter, BaseSplitter

logger = logging.getLogger(__name__)


class PythonAction(SingleActionBase):
    """Action that offers a generic wrapper around any python callable. The basic idea is to have a simple possibility
     to define action that execute a python script. The python script that should be executed must be passed as callable.
     The action will call the callable with the following arguments:
     1. all unknown keyword arguments that are passed to the action (inputArgs).
     2. **additionalArgs
     3. an argument called "outputs", that contain the result of self.indicateOutputs.
     For the input arguments the user of the action is free to use any keyword that is not reserved by the action and is
     not "outputs". Additionally the action checks name collisions of inputArgs and additionalArgs and will raise an
     exception if needed.
     :param generateCallable: A callable that will be called to generate the outputs. The action assumes that all outputs
     are generated and stored at their designated location.
     :param indicateCallable: A callable that, if defined, will be called (like generateCallable) to query the outputs.
     The action assumes that the callable returns a list of output artefacts or None (if no indication can be made; like
     self.indicateOutputs). If this callable is not set, the default is one output that will be defined by the action
     and uses the first input artefact as reference. The signature of indicateCallable is:
     indicateCallable(actionInstance ( = Instance of the calling action), **allArgs
      (= all arguments passed to the action)
     :param outputReferenceArtefactName: Name of the inputArgs that will be used as
        template when generating the output artefacts. If not set (None), the first input selection (in alphabetic
        order) will be used. If indicateCallable is set, this argument has only impact if the callable makes use of it.
     :param additionalArgs: Dictionary containing all arguments that should be passed to generateCallable and are no
      artefact input arguments.
     :param passOnlyURLs: If set to true only URLs of the artefacts, instead of the artefacts themself, will be passed to
      generateCallable.
     :param defaultoutputextension: Output extension that should be used if no indicateCallable is defined.
     :param inputArgs: It is assumed that all unkown named arguments are inputs with artefact lists."""

    OUTPUTS_ARGUMENT_NAME = 'outputs'

    def __init__(self, generateCallable, indicateCallable=None, additionalArgs=None, passOnlyURLs=True,
                 defaultoutputextension='nrrd', outputReferenceArtefactName=None,
                 actionTag="Python", alwaysDo=True, session=None, additionalActionProps=None,
                 propInheritanceDict=None, **inputArgs):
        SingleActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps,
                                  propInheritanceDict=propInheritanceDict)
        self._generateCallable = generateCallable
        self._indicateCallable = indicateCallable
        self._passOnlyURLs = passOnlyURLs
        self._outputextension = defaultoutputextension

        self._inputArgs = dict()
        self._args = dict()
        self._resultArtefacts = None

        if additionalArgs is not None:
            for name in additionalArgs:
                if name == self.OUTPUTS_ARGUMENT_NAME:
                    raise ValueError(
                        'Additional argument used reserved arguments name. Reserved name: {}'.format(
                            self.OUTPUTS_ARGUMENT_NAME))
                self._args[name] = additionalArgs[name]

        for name in inputArgs:
            inputArtefacts = self._ensureArtefacts(inputArgs[name], name=name)
            if inputArtefacts is None:
                raise ValueError(
                    'Input argument is invalid as it does not contain artefact instances or is None/empty. Input name: {}'.format(
                        name))
            if additionalArgs is not None and name in additionalArgs:
                raise ValueError(
                    'Input argument name is also defined as additional argument. Name may only by used for inputs or'
                    ' additional arguments. Input name: {}'.format(
                        name))
            if name == self.OUTPUTS_ARGUMENT_NAME:
                raise ValueError(
                    'Input argument used reserved arguments name. Reserved name: {}'.format(self.OUTPUTS_ARGUMENT_NAME))
            self._inputArgs[name] = inputArtefacts

        self._addInputArtefacts(**self._inputArgs)

        if len(self._inputArgs) == 0:
            raise RuntimeError('Action is not initialized with any artefact inputs')

        self._outputReferenceArtefactName = outputReferenceArtefactName
        if self._outputReferenceArtefactName is not None:
            if self._outputReferenceArtefactName not in self._inputs:
                raise ValueError(
                    'Action cannot be initialized. Defined outputReferenceArtefactName ("{}") does not exist in the inputs dictionary: {}'.format(
                        self._outputReferenceArtefactName, self._inputs.keys()))


    def _generateName(self):
        name = 'script'
        try:
            name = self._generateCallable.__name__
        except:
            try:
                name = self._generateCallable.__class__.__name__
            except:
                pass
        return name

    def _indicateOutputs(self):
        if self._indicateCallable is not None:
            allargs = self._inputArgs.copy()
            allargs.update(self._args)
            self._resultArtefacts = self._indicateCallable(actionInstance=self, **allargs)
            if self._resultArtefacts is not None:
                # check if its really a list of artefacts
                try:
                    for artifact in self._resultArtefacts:
                        if not isinstance(artifact, artefactHelper.Artefact):
                            raise TypeError(
                                'Indicate callable does not return a list of artefacts. Please check callable. Erroneous return: {}'.format(
                                    self._resultArtefacts))
                except:
                    raise TypeError(
                        'Indicate callable does not return a list of artefacts. Please check callable. Erroneous return: {}'.format(
                            self._resultArtefacts))
        else:
            # we generate the default as template the first artefact of the first input (sorted by input names) in the dictionary
            reference = self._inputArtefacts[sorted(self._inputArtefacts.keys())[0]][0]

            if self._outputReferenceArtefactName is not None:
                reference = self._inputArtefacts[self._outputReferenceArtefactName][0]

            self._resultArtefacts = [
                self.generateArtefact(reference=reference,
                                      userDefinedProps={artefactProps.TYPE: artefactProps.TYPE_VALUE_RESULT},
                                      urlHumanPrefix=self.instanceName,
                                      urlExtension=self._outputextension)]
        return self._resultArtefacts

    def _generateOutputs(self):
        allargs = self._args.copy()

        if self._resultArtefacts is not None:
            outputs = list()
            for output in self._resultArtefacts:
                if self._passOnlyURLs:
                    outputs.append(artefactHelper.getArtefactProperty(output, artefactProps.URL))
                else:
                    outputs.append(output)
            allargs[self.OUTPUTS_ARGUMENT_NAME] = outputs

        for name in self._inputArgs:
            if self._passOnlyURLs:
                if isinstance(self._inputArgs[name], artefactHelper.Artefact):
                    allargs[name] = artefactHelper.getArtefactProperty(self._inputArgs[name], artefactProps.URL)
                else:
                    # assuming a list of artefacts
                    inputURLs = list()
                    for artefact in self._inputArgs[name]:
                        inputURLs.append(artefactHelper.getArtefactProperty(artefact, artefactProps.URL))
                    allargs[name] = inputURLs
            else:
                allargs[name] = self._inputArgs[name]

        if self._resultArtefacts is not None:
            destPath = artefactHelper.getArtefactProperty(self._resultArtefacts[0], artefactProps.URL)
            checkAndCreateDir(os.path.dirname(destPath))

        try:
            self._generateCallable(**allargs)
        except BaseException as e:
            self._reportWarning('Error occurred while trying to execute custom python callable to generated outputs for'
                                f' action tag "{self.actionTag}".'
                                ' Check the implementation of the generateCallable passed to action class'
                                f' "{self.__class__}" to.', exception=e)
            raise



class PythonUnaryBatchAction(BatchActionBase):
    '''Batch class that assumes only one input artefact that will be passed to the script.'''

    def __init__(self, inputSelector, actionTag="UnaryScript", session=None, additionalActionProps=None,
                 scheduler=SimpleScheduler(), **singleActionParameters):
        BatchActionBase.__init__(self, actionTag=actionTag, actionClass=PythonAction,
                                 primaryInputSelector=inputSelector,
                                 primaryAlias="inputs", session=session,
                                 relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps=additionalActionProps,
                                 **singleActionParameters)


class PythonBinaryBatchAction(BatchActionBase):
    '''Batch class that assumes two input artefacts (joined by an (optional) linker) will be passed to the script.
     The batch class assumes that the python script takes the inputs as arguments "inputs1" and "inputs2".'''

    def __init__(self, inputs1Selector, inputs2Selector, inputLinker=None, actionTag="BinaryScript",
                 session=None, additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
        if inputLinker is None:
            inputLinker = CaseLinker()

        additionalSelectors = {'inputs2': inputs2Selector}
        linker = {"inputs2": inputLinker}

        BatchActionBase.__init__(self, actionTag=actionTag, actionClass=PythonAction,
                                 primaryInputSelector=inputs1Selector,
                                 primaryAlias="inputs1", additionalInputSelectors=additionalSelectors, linker=linker,
                                 session=session, relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps=additionalActionProps,
                                 **singleActionParameters)


class PythonNaryBatchAction(BatchActionBase):
    '''Batch class that assumes an arbitrary number (>= 1) of input artefacts will be passed to the script.
     The class assumes the following:
     - inputsMaster is the selector that defines the master artefacts (other artefacts will be linked against them).
     - all named unkown arguments that are passed with init and start with the prefix "inputs" are additional input selectors.
     - all named unkown arguments that have the same name like and additional input and have the suffix "Linker" are
      linker for the input. The linker will be used to link its input against the master input.
     - if an input has no linker specified, CaseLinker+CaseInstanceLinker will be assumed.
     - The additional inputs are not linked against each other. So all combinations of additional inputs for a master
      input is processed.
     The batch class assumes that the python script takes
     - the master input as "inputsMaster"
     - all other inputs with the name they where passed to the batch action.
     REMARK: If you want a batch action that allows more control over the callable's argument namings and is
     close to the interface of the BatchActionBase, please see PythonNaryBatchActionV2.'''

    def __init__(self, inputsMaster, actionTag="NaryScript",
                 session=None, additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):

        otherSelectors = dict()
        otherLinker = dict()
        newSingleActionParameters = dict()

        for paramName in singleActionParameters:
            if paramName.startswith('inputs'):
                if paramName.endswith('Linker'):
                    otherLinker[paramName[:-6]] = singleActionParameters[paramName]
                else:
                    otherSelectors[paramName] = singleActionParameters[paramName]
            else:
                newSingleActionParameters[paramName] = singleActionParameters[paramName]

        for inputName in otherSelectors:
            if not inputName in otherLinker:
                otherLinker[inputName] = CaseLinker() + CaseInstanceLinker()

        BatchActionBase.__init__(self, actionTag=actionTag, actionClass=PythonAction, primaryInputSelector=inputsMaster,
                                 primaryAlias="inputsMaster", additionalInputSelectors=otherSelectors,
                                 linker=otherLinker, session=session,
                                 relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps=additionalActionProps,
                                 **newSingleActionParameters)


class PythonNaryBatchActionV2(BatchActionBase):
    """New python batch class that assumes an arbitrary number (>= 1) of input artefacts will be passed to the script.
    In contrast to PythonNaryBatchAction, this class makes no assumption about the namings of selectors, linkers and
    co. Thus you can specify them freely and are not bound to any conventions for your python callable's argument names.
    In addition this class also allows to specify the splitter and sorter explicitly."""

    def __init__(self, primaryInputSelector, actionTag="NaryScript",
                 primaryAlias = None, additionalInputSelectors = None, splitter = None, sorter = None, linker = None,
                 dependentLinker = None, session=None, additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
        """init the action and setting the workflow session, the action is working
          in.
          :param actionTag: Tag of the action within the session
          :param additionalActionProps: Dictionary that can be used to define additional
          properties that should be added to any artefact that are produced by the action.
          :param primaryInputSelector: Selector that indicates the primary input for the actions that should be generated
          :param primaryAlias: Name of the primary input that should be used as argument key if passed to action.
          If not set PRIMARY_INPUT_KEY will be used.
          :param additionalInputSelectors: Dictionary containing additional input selectors for other inputs that should
          be passed to an action instance. Key is the name of an additional input an also the argument name used to pass
          the input to the action instance. The associated dict value must be a selector instance or None to indicate
          that this input will have no data but exists.
          :param splitter: Dictionary specifying a splitter that should be used for a specific input (primary or additional)
          If no splitter is defined explicitly for an input SingleSplitter() will be assumed. The key indicates the
          input that should be associated with the splitter. To associate primary input use PRIMARY_INPUT_KEY as key.The
          values of the dict are the splitter instances that should be used for the respective key.
          :param sorter: Dictionary specifying a sorter that should be used for a specific input (primary or additional)
          If no sorter is defined explicitly for an input, BaseSorter() (so no sorting at all) will be assumed.
          The key indicates the input that should be associated with the sorter. To associate primary input use
          PRIMARY_INPUT_KEY as key. The values of the dict are the sorter instances that should be used for the
          respective key.
          :param linker: Dictionary specifying a linker that should be used for a specific additional input
          to link it with the primary input. Thus the master selection passed to the linker will always be provided by
          the primary input.
          If no linker is defined explicitly for an input CaseLinker() (so all inputs must have the same case) will be
          assumed. The key indicates the input that should be associated with the linker. The values of the dict are the
          linker instances that should be used for the respective key.
          :param dependentLinker: Allows to specify linkage for an additional input where the master selection must not
          be the primary input (in contrast to using the linker argument). Thus you can specifies that an additional
          input A is (also) linked to an additional input B. The method assumes the following structure of the variable.
          It is a dictionary. The dictionary key indicates the input that should be linked. So it can be any additional
          input. It must not be the primary input. The value associated with a dict key is an iterable (e.g. list) the
          first element is the name of the input that serves as master for the linkage. It may be any additional input
          (except itself = key of the value) or the primary input. The second element is the linker instance that should
          be used. You may combine linker and dependentLinker specifications for any additional input.
          To associate primary input as master use PRIMARY_INPUT_KEY as value.
          :param session: Session object of the workflow the action is working in
          :param scheduler Strategy how to execute the single actions.
        """
        BatchActionBase.__init__(self, primaryInputSelector=primaryInputSelector, actionTag=actionTag,
                                 primaryAlias=primaryAlias, actionClass=PythonAction,
                                 additionalInputSelectors=additionalInputSelectors,splitter=splitter,
                                 sorter=sorter, linker=linker, dependentLinker=dependentLinker, session=session,
                                 additionalActionProps=additionalActionProps,scheduler=scheduler,
                                 **singleActionParameters)


class PythonUnaryStackBatchAction(BatchActionBase):
    '''Batch class that assumes a list of input artefacts will be passed to the script.
    The list of artefacts is defined via the input selector.
    @param splitProperties You can define a list of split properties (list of property names)
    to separate it into different actions (e.g. like the PixelDumpMiniApp action.
    '''

    def __init__(self, inputSelector, splitProperties=None, actionTag="UnaryStackScript",
                 session=None, additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
        splitter = {BatchActionBase.PRIMARY_INPUT_KEY: BaseSplitter()}
        if splitProperties is not None:
            splitter = {BatchActionBase.PRIMARY_INPUT_KEY: KeyValueSplitter(*splitProperties)}
        BatchActionBase.__init__(self, actionTag=actionTag, actionClass=PythonAction,
                                 primaryInputSelector=inputSelector,
                                 primaryAlias="inputs", splitter=splitter, session=session,
                                 relevanceSelector=TypeSelector(artefactProps.TYPE_VALUE_RESULT),
                                 scheduler=scheduler, additionalActionProps=additionalActionProps,
                                 **singleActionParameters)
