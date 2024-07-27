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
import threading
from builtins import str
from builtins import object
import os
import logging
import time
import uuid

import avid.common.artefact.generator as artefactGenerator
import avid.common.artefact as artefactHelper
import avid.common.artefact.defaultProps as artefactProps
from .simpleScheduler import SimpleScheduler
import avid.common.workflow as workflow
from .actionBatchGenerator import ActionBatchGenerator
from ..selectors import ActionTagSelector

logger = logging.getLogger(__name__)

class ActionBase(object):
    '''Base class for action objects used in AVID to do any kind of processing with/on artefacts.'''

    """Indicating the success of the (last) execution of an action instance."""
    ACTION_SUCCESS = "SUCCESS"
    """Indicating the failure of the (last) execution of an action instance."""
    ACTION_FAILURE = "FAILURE"
    """Indicating the skipping of the (last) execution of an action. As any outputs the action instance
    would produce are available and still up to date."""
    ACTION_SKIPPED = "SKIPPED"
    """Indicating that the action instance was not executed so far."""
    ACTION_PENDING = "PENDING"

    def __init__(self, actionTag, session=None, additionalActionProps=None):
        '''init the action and setting the workflow session, the action is working
          in.
          @param session: Session object of the workflow the action is working in
          @param actionTag: Tag of the action within the session
          @param additionalActionProps: Dictionary that can be used to define additional
          properties that should be added to any artefact that are produced by the action.
        '''

        self._instanceUID = uuid.uuid4()
        self._init_session(session)
        self._actionTag = actionTag

        self._additionalActionProps = additionalActionProps
        if self._additionalActionProps is None:
            self._additionalActionProps = {}

        self._outputArtefacts = None
        self._last_exec_state = self.ACTION_PENDING

        #list of all warnings captured since the last execution of the action. Elements of this list are
        #pair tuples of detail strings and exception instances (if provided; if not provided the 2nd
        #value is None).
        self._last_warnings = list()

    @property
    def actionTag(self):
        return self._actionTag

    @property
    def actionTagSelector(self):
        return ActionTagSelector(self._actionTag)

    @property
    def actionInstanceUID(self):
        return str(self._instanceUID)

    @property
    def outputArtefacts(self):
        if self._outputArtefacts is None and self.isPending:
            self.indicateOutputs()
        return self._outputArtefacts

    @property
    def last_exec_state(self):
        return self._last_exec_state

    @property
    def last_warnings(self):
        return self._last_warnings

    @property
    def has_warnings(self):
        return len(self._last_warnings) > 0

    @property
    def isSuccess(self):
        return self._last_exec_state == self.ACTION_SUCCESS

    @property
    def isFailure(self):
        return self._last_exec_state == self.ACTION_FAILURE

    @property
    def isSkipped(self):
        return self._last_exec_state == self.ACTION_SKIPPED

    @property
    def isPending(self):
        return self._last_exec_state == self.ACTION_PENDING

    def _init_session(self, session = None):
        if session is None:
            # check if we have a current generated global session we can use
            if workflow.currentGeneratedSession is not None:
                self._session = workflow.currentGeneratedSession
            else:
                raise ValueError("Session passed to the action is invalid and no global session found."
                                 "Cannot init action.")
        else:
            self._session = session

    def indicateOutputs(self):
        ''' Return a list of artefact entries the action will produce if do() is
          called. The method should return complete entries.
          Therefore, the entries should already contain the url where they
          *will* be stored if the action is executed.
          Remark: The output indication might not represent the final result of an action
          (e.g. because an action is not able to determine the outputs before they are actually
          generated.). This the list might only indicate the assumed outputs. Also An action can return
          None to signal that it cannot indicate the outputs before generation.
          :return: Either a list of indicated outputs or None.'''
        if self._outputArtefacts is None and self.isPending:
            self._outputArtefacts = self._indicateOutputs()

        return self._outputArtefacts

    def _indicateOutputs(self):
        ''' Internal function that is called by indicate outputs if no output artefact
          list exists yet. Return a list of artefact entries the action will produce
          if do() is called. The method should
          return complete entries. Therefore the entries should already contain the
          url where they *will* be stored if the action is executed.'''
        raise NotImplementedError("Reimplement in a derived class to function correctly.")
        # Implement: return a list of valid artefact entries
        pass

    @property
    def instanceName(self):
        return self._generateName()

    def _generateName(self):
        ''' Internal function that generates a name for the current action instance
          based on its configuration and input artefacts.'''
        raise NotImplementedError("Reimplement in a derived class to function correctly.")
        pass

    def _do(self):
        ''' Internal function that triggers the processing of an action.
          This Method is used internally (e.g. when ever an action is used by an other
          action; and no action tag should be added to the session. '''
        raise NotImplementedError("Reimplement in a derived class to function correctly.")
        # Implement: what the action should really do
        pass

    def do(self):
        '''Triggers the processing of an action instance. This should be used as public
        trigger of an action.'''
        global logger
        logger.info("Starting action: " + self.instanceName + " (UID: " + self.actionInstanceUID + ") ...")

        self._last_warnings = list()

        (self._last_exec_state, self._outputArtefacts) = self._do()

        logger.info(f"Finished action: {self.instanceName} (UID: {self.actionInstanceUID}) -> {self._last_exec_state}")
        self._notifyActionFinished()
        return self._last_exec_state

    def _reportWarning(self, details, exception=None):
        """Helper function that is used to report a warning happening in an action.
        @param details: string containing the details for that warning that should be
        reported.
        @param exception: If the warning was detected due to an exception it can also be passed
        with this parameter."""
        self._last_warnings.append((details, exception))
        logger.warning(details)

    def _notifyActionFinished(self):
        """Method that is called by do() to signal the session that a certain action is finished.
        Default implementation does nothing."""
        pass

class SingleActionBase(ActionBase):
    '''Base class for action that directly will work on artefact and generate them.'''

    def __init__(self, actionTag, alwaysDo=False, session=None, additionalActionProps=None, propInheritanceDict=None):
        '''init the action and setting the workflow session, the action is working
          in.
          @param session: Session object of the workflow the action is working in
          @param actionTag: Tag of the action within the session
          @param alwaysDo: Indicates if the action should generate its artefacts even
          if they already exist in the workflow (True) or if the action should skip
          the processing (False).
          @param additionalActionProps: Dictionary that can be used to define additional
          properties that should be added to any artefact that are produced by the action.
          Remark: properties defined here will always override the propInheritanceDict.
          @param propInheritanceDict: Dictionary that can be used to define if and who
          properties of the inputs are inherited to artefacts generated by
          SingelActionBase.generateArtefact(). The key of the dict defines the property
          for which a value is inherited. The value defines the input (key in self._inputArtefacts).
        '''
        ActionBase.__init__(self, actionTag=actionTag, session=session, additionalActionProps=additionalActionProps)

        self._alwaysDo = alwaysDo
        # CaseInstance that should all artefacts generated by this action have
        self._caseInstance = None

        self._inputArtefacts = dict()

        self._propInheritanceDict = propInheritanceDict
        if self._propInheritanceDict is None:
            self._propInheritanceDict = dict()

    def _ensureSingleArtefact(self, artefacts, name):
        """Helper method that can be used by actions that only handle one artefact as a specific input."""
        if artefacts is None:
            return None
        if len(artefacts) == 0:
            return None
        from avid.common.artefact import Artefact
        if isinstance(artefacts, Artefact):
            return artefacts
        if len(artefacts) > 1:
            self._reportWarning('Action class {} only supports one artefact as {}. Use first one.'.format(self.__class__.__name__, name))
        return artefacts[0]

    def _ensureArtefacts(self, artefacts, name):
        """Helper method that can be used by actions to ensure that a list of artefacts was passed or None."""
        if artefacts is None:
            return None
        if len(artefacts) == 0:
            return None
        from avid.common.artefact import Artefact
        if isinstance(artefacts, Artefact):
            self._reportWarning('Action {} was init in an deprecated style for input "{}"; not an list of artefacts'
                               ' where passed but only an artefact. Check usage. Illegal artefact: {}.'.format(
                    self.__class__.__name__, name, artefacts))
            return [artefacts]
        for artefact in artefacts:
            if artefact is not None and not isinstance(artefact, Artefact):
                self._reportWarning(
                    'An instance that is not of class Artefact was passed to the action {} as {}.'
                    ' Illegal element: {}.'.format(self.__class__.__name__, name, artefact))
                return None

        return artefacts

    def _addInputArtefacts(self, **inputs):
        '''This function should be used in the init of derived actions to register
        artefacts as input artefacts for the action instance. This will be used for several
        things; e.g. determining the Caseinstance of the action instance, used in the
        generation of new artefacts, used to determine if outputs can be generated.
        The class assumes that the inputs passed are a list of artefacts for each input key/channel.
        Empty lists or none channels will node be added.'''
        for iKey in inputs:
            if inputs[iKey] is not None and len(inputs[iKey])>0:
                self._inputArtefacts[iKey] = inputs[iKey]

        self._setCaseInstanceByArtefact(self._inputArtefacts)

    def _setCaseInstanceByArtefact(self, inputArtefacts):
        '''defines the case instance used by the action based on the passed input artefact.'''
        stubArtefact = dict()
        stubArtefact[artefactProps.CASEINSTANCE] = None
        for inputKey in inputArtefacts:
            if not artefactHelper.ensureCaseInstanceValidity(stubArtefact, *inputArtefacts[inputKey]):
                self._reportWarning('Case instance conflict raised by the input artefact of the action.'
                                   ' Input artefacts {}'.format(inputArtefacts))

        self._caseInstance = stubArtefact[artefactProps.CASEINSTANCE]

    # noinspection PyProtectedMember
    def generateArtefact(self, reference=None, copyAdditionalPropsFromReference=True, userDefinedProps = None,
                         urlHumanPrefix = None, urlExtension = None):
        '''Helper method that can be used in derived action classes in their
        indicateOutputs() implementation. The generation will be done in following
        steps:
        1) It generates an artefact that has the actionTag of the current action.
        2) Other properties will be taken from the reference (if given).
        3) If a self._propInheritanceDict is specified it will be used to inherit property values.
        4) self._additionalActionProps will be transferd.
        5) the property values defined in userDefinedProps will be transfered.
        Remark: ActionTag will always be of this action.
        Remark: As default the URL will be None. If parameter urlHumanPrefix or urlExtension are not None, an artefact
        URL will be created. In this case the following pattern will be used:
        <artefact_path>[<urlHumanPrefix>.]<artefact_id>[<><urlExtension>]
        artefact_path: Return of artefactHelper.generateArtefactPath using the configured new artefact.
        urlHumanPrefix: Parameter of the call
        artefact_id: ID of the new artefact
        extension_seperator: OS specific file extension seperator
        urlExtension: Parameter of the call
        REMARK: Currently if self has a _propInheritanceDict specified, only the first artefact of the indicated
        input selection will be used to inherit the property.
        @param reference An other artefact as reference. If given, the following
        properties will be copied to the new artefact: Case, timepoint,
        type, format, objective.
        @param copyAdditionalPropsFromReference Indicates if also the additional properties should be
        transfered from the reference to the new artefact (only relevant of reference is not None).
        @param userDefinedProps Properties specified by the user that should be set for the new artefact.
        Parameter is a dictionary. The keys are the property ids and the dict values their value. Passing None indicates
        that there are no props
        @urlHumanPrefix: specifies the humand readable prefix of the artefact url. If set a URL will be generated.
        @urlExtension: specifies the file extension of the artefact url. If set a URL will be generated.'''
        result = artefactGenerator.generateArtefactEntry(
            artefactHelper.getArtefactProperty(reference, artefactProps.CASE),
            self._caseInstance,
            artefactHelper.getArtefactProperty(reference, artefactProps.TIMEPOINT),
            self._actionTag,
            artefactHelper.getArtefactProperty(reference, artefactProps.TYPE),
            artefactHelper.getArtefactProperty(reference, artefactProps.FORMAT),
            None,
            artefactHelper.getArtefactProperty(reference, artefactProps.OBJECTIVE),
            action_class = self.__class__.__name__,
            action_instance_uid = self.actionInstanceUID,
            result_sub_tag = artefactHelper.getArtefactProperty(reference, artefactProps.RESULT_SUB_TAG))

        for propID in self._propInheritanceDict:
            if not propID == artefactProps.ACTIONTAG \
                    and not propID == artefactProps.CASEINSTANCE \
                    and not propID == artefactProps.URL:
                try:
                    if propID in self._inputArtefacts[self._propInheritanceDict[propID]][0]:
                        result[propID] = artefactHelper.getArtefactProperty(self._inputArtefacts[self._propInheritanceDict[propID]][0],propID)
                    if len(self._inputArtefacts[self._propInheritanceDict[propID]])>1:
                        self._reportWarning('Input {} has more then one artefact. Use only first artefact to inherit'
                                           ' property "{}". Used artefact: {}'
                                            .format(self._propInheritanceDict[propID], propID,
                                                   self._inputArtefacts[self._propInheritanceDict[propID]][0]))
                except:
                    pass

        for propID in self._additionalActionProps:
            if not propID == artefactProps.ACTIONTAG \
                    and not propID == artefactProps.CASEINSTANCE \
                    and not propID == artefactProps.URL:
                result[propID] = self._additionalActionProps[propID]

        if reference is not None and copyAdditionalPropsFromReference:
            k1 = list(result._additionalProps.keys())
            k2 = list(reference._additionalProps.keys())
            additionalKs = [x for x in k2 if x not in k1]

            for k in additionalKs:
                result[k] = reference[k]

        if userDefinedProps is not None:
            for propID in userDefinedProps:
                try:
                    result[propID] = userDefinedProps[propID]
                except:
                    pass

        if urlHumanPrefix is not None or urlExtension is not None:
            path = artefactHelper.generateArtefactPath(self._session, result)
            name = ""
            if urlHumanPrefix is not None:
                name = urlHumanPrefix + "."
            name = name + str(artefactHelper.getArtefactProperty(result, artefactProps.ID))

            if urlExtension is not None:
                name = name + os.extsep + urlExtension

            name = os.path.join(path, name)

            result[artefactProps.URL] = name

        inputs = dict()
        for inputName in self._inputArtefacts:
            iaIDs = list()
            for ia in self._inputArtefacts[inputName]:
                iaIDs.append(artefactHelper.getArtefactProperty(ia,artefactProps.ID))
            inputs[inputName] = iaIDs
        if len(inputs)>0:
            result[artefactProps.INPUT_IDS] = inputs
        else:
            result[artefactProps.INPUT_IDS] = None

        return result

    def _generateOutputs(self):
        ''' Internal execution method of any action. This method should be
          reimplemented in derived classes to do the real work.
          @postcondition: all artefacts indicated by indicateOutputs are correctly created
          and do exist.
          @remark It is *not* needed to add the artefacts to the session or something
          else. This all will be handled by the calling do() method.'''
        raise NotImplementedError("Reimplement in a derived class to function correctly.")
        # Implement: do the action job and generate all artefacts indicated by indicateOutputs,
        # so that they exist after returning from this function.
        pass

    def _checkNecessity(self, outputs):
        '''Checks if the workflow already contains the outputs of type 'result' in a valid state.
          @param outputs: Entries that would be generated by the action.
          @return Tupple: 1. indicating if action should run. 2. list of all entries
          that are valid and already available. If 1st is True the list has alternatives
          for all outputs.'''
        global logger
        needed = False
        alternatives = list()

        for output in outputs:
            if artefactHelper.getArtefactProperty(output, artefactProps.TYPE) == artefactProps.TYPE_VALUE_RESULT:
                alternative = artefactHelper.findSimilarArtefact(self._session.artefacts, output)
                if alternative is None \
                        or alternative[artefactProps.INVALID] \
                        or alternative[artefactProps.URL] is None \
                        or not os.path.isfile(alternative[artefactProps.URL]):
                    needed = True
                else:
                    alternatives += alternative,
                    logger.debug("Valid alternative already exists. Indicated output: %s; alternative: %s", str(output),
                                 str(alternative))

        return (needed, alternatives)

    def _checkOutputsExistance(self, outputs):
        '''Checks if the given artefacts exists as file. Outputs that do not exist
          are marked as invalid.
          :return: a tuple as result. 1st value indicates if all outputs are valid. 2nd value is the
          output list with updated validity state.'''
        valid = not len(outputs) == 0

        result = list()
        for output in outputs:
            if os.path.isfile(output[artefactProps.URL]):
                output[artefactProps.INVALID] = False
            else:
                output[artefactProps.INVALID] = True
                valid = False
                global logger
                logger.info("Generated output is invalid and marked as such. Invalid output: %s", str(output))
            result += output,

        return (valid, result)

    def _collectOutputs(self, indicatedOutputs):
        '''Function that is offers the possibility after generateOutput() to verify/collect the outputs produced be
         generate output. Default implementation does nothing and assumes that indicatedOutputs is already correct
         (classic default behavior). This function can be used be derived classes to implement actions, that only
         can determine their outputs after generation.
         :return: List of the outputs generated by the action execution.'''
        if indicatedOutputs is None:
            raise RuntimeError('Action has indicated no outputs (indicatedOutputs is None), but uses default'
                               ' implementation of _collectOutputs(). Either _indicatedOutputs is wrongly implemented'
                               ' or (if None is correct) you need to implement your own _collectOutputs() to gather'
                               ' the outputs after generation. Wrong action class instance: {}'.format(self))
        return indicatedOutputs

    def _getInvalidInputs(self):
        '''Helper function that checks if registered inputs for the action are invalid.
          :return: Returns a dict with all invalid inputs. An empty dict indicates that all inputs are valid.'''

        invalidInputs = dict()

        for key in self._inputArtefacts:
            if not self._inputArtefacts[key] is None:
                for artefact in self._inputArtefacts[key]:
                    if artefact is not None and artefact.is_invalid():
                        invalidInputs[key] = self._inputArtefacts[key]
                        break;

        return invalidInputs

    def _do(self):
        ''' Triggers the processing of an action. '''
        global logger

        outputs = self.indicateOutputs()
        (isNeeded, alternatives) = self._checkNecessity(outputs)

        state = ActionBase.ACTION_SUCCESS

        if self._alwaysDo or isNeeded:
            isValid = False
      
            starttime = time.time()
            endtime = None
            
            invalidInputs = self._getInvalidInputs()
            if len(invalidInputs) == 0:
                failure_occurred = False
                try:
                    self._generateOutputs()
                    endtime = time.time()
                except BaseException as e:
                    self._reportWarning(f'Error occurred while generating outputs for action tag "{self.actionTag}".'
                                        ' The error occurred in the class specific implementation of the'
                                        f' _generateOutputs method of "{self.__class__}". Please check the'
                                        ' implementation of the method or the class documentation.'
                                        f' All outputs will be marked as invalid. Error details: {str(e)}'
                                        , exception=e)
                    failure_occurred = True
                except:
                    self._reportWarning('Unknown error occurred while generating outputs for action tag'
                                        f' "{self.actionTag}".'
                                        ' The error occurred in the class specific implementation of the'
                                        f' _generateOutputs method of "{self.__class__}". Please check the'
                                        ' implementation of the method or the class documentation.'
                                        ' All outputs will be marked as invalid.')
                    failure_occurred = True

                if not failure_occurred:
                    try:
                        outputs = self._collectOutputs(indicatedOutputs = outputs)
                        (isValid, outputs) = self._checkOutputsExistance(outputs)
                    except BaseException as e:
                        self._reportWarning('Error occurred while collecting generated outputs for action tag'
                                            f' "{self.actionTag}".'
                                            f' If the action class "{self.__class__}" has a specific implementation of the'
                                            f' _collectOutputs method, please check the'
                                            ' implementation of the method or the class documentation.'
                                            f' All outputs will be marked as invalid. Error details: {str(e)}'
                                            , exception=e)
                        failure_occurred = True
                    except:
                        self._reportWarning('Unknown error occurred while collecting generated outputs for action tag'
                                            f' "{self.actionTag}".'
                                            f' If the action class "{self.__class__}" has a specific implementation of the'
                                            f' _collectOutputs method, please check the'
                                            ' implementation of the method or the class documentation.'
                                            ' All outputs will be marked as invalid.')
                        failure_occurred = True

            else:
                self._reportWarning('Action failed due to at least one invalid input. All outputs are marked as invalid.'
                                    ' Typical reason for that error is that a preceding action (that generated inputs)'
                                    ' failed and generated the invalid inputs.'
                                    ' Invalid inputs: {}'.format(self._inputArtefacts))

            if not isValid:
                for artefact in outputs:
                    artefact[artefactProps.INVALID] = True

            generatedArtefacts = outputs
      
            for artefact in outputs:
                try:
                    artefact[artefactProps.EXECUTION_DURATION] = endtime - starttime
                except:
                    pass
        
                self._session.addArtefact(artefact, True)

            if not isValid:
                state = ActionBase.ACTION_FAILURE

        else:
            generatedArtefacts = alternatives
            state = ActionBase.ACTION_SKIPPED

        return (state, generatedArtefacts)

    def _notifyActionFinished(self):
        """Method that is called by do() to signal the session that a certain action is finished.
        Default implementation does nothing."""
        self._session.addProcessedActionInstance(self)

class BatchActionBase(ActionBase):
    '''Base class for action objects that resemble the logic to generate and
       to process a batch of SingleActionBased actions based ond the current session and the given selectors, sorters,
       linkers, splitters.'''

    PRIMARY_INPUT_KEY = ActionBatchGenerator.PRIMARY_INPUT_KEY

    def __init__(self, actionTag, primaryInputSelector, actionClass = None, actionCreationDelegate = None,
                 primaryAlias = None, additionalInputSelectors = None, splitter = None, sorter = None, linker = None,
                 dependentLinker = None, session=None, relevanceSelector = None, additionalActionProps = None,
                 scheduler=SimpleScheduler(), **actionParameters, ):
        '''init the action and setting the workflow session, the action is working
          in.
          :param actionTag: Tag of the action within the session
          :param additionalActionProps: Dictionary that can be used to define additional
          properties that should be added to any artefact that are produced by the action.
          :param actionClass: Class of the action that should be generated
          :param actionCreationDelegate: Callable delegate that, if set, will be used to generate the action classes.
          Either actionClass or actionCreationDelegate have to be set; but only one of them. ActionBatchGenerator
          assumes that the delegate returns a list of generate action instances. The delegate will be called like the
          action class. A delegate can be used to manipulate the generation of the action instances after the whole
          splitting, sorting, selecting and linking is done.
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
          :param relevanceSelector: Selector used to specify for all inputs of actions what is relevant. If not set
          it is assumed that only artefact of type TYPE_VALUE_RESULT are relevant.
          :param session: Session object of the workflow the action is working in
          :param scheduler Strategy how to execute the single actions.
        '''
        ActionBase.__init__(self, actionTag, session, additionalActionProps)
        self._actions = None
        self._scheduler = scheduler  # scheduler that should be used to execute the jobs
        self._session.registerBatchAction(self)

        self.lock = threading.RLock()

        actionParameters["actionTag"] = actionTag
        actionParameters["additionalActionProps"] = additionalActionProps

        self._generator = ActionBatchGenerator(actionClass= actionClass, primaryInputSelector = primaryInputSelector,
                                               actionCreationDelegate=actionCreationDelegate, primaryAlias= primaryAlias,
                                               additionalInputSelectors=additionalInputSelectors, splitter=splitter,
                                               sorter=sorter, linker=linker, dependentLinker=dependentLinker,
                                               session=session, relevanceSelector=relevanceSelector, **actionParameters)


    def _generateName(self):
        return self.__class__.__name__ + "_" + str(self.actionTag)

    def _indicateOutputs(self):
        ''' Return a list of artefact entries the action will produce if do() is
          called. Reimplement this method for derived actions. The method should
          return complete entries. Therefore the enties should already contain the
          url where they *will* be stored if the action is executed.'''
        self.generateActions()

        outputs = list()

        for action in self._actions:
            outputs += action.indicateOutputs()

        return outputs

    def generateActions(self):
        """ Function that (pre)generates the actions of the batch action.
        If actions are already generated, nothing will happen."""
        if self._actions is None:
            with self.lock:
                self._actions = self._generateActions()

    def _generateActions(self):
        ''' Internal method that should generate all single actions that should be
          executed and returns them in a list. This method should be
          reimplemented in derived classes to do the real work of dispatching the
          selectors and creating the action functors for all needed actions.
          @postcondition: all needed single actions are created and configured to be
          read to be executed.'''
        return self._generator.generateActions()

    def _do(self):
        ''' Triggers the processing of an action. '''

        self.generateActions()

        self._scheduler.execute(self._actions)

        state = ActionBase.ACTION_SKIPPED
        generatedArtefacts = list()

        with self.lock:
            for action in self._actions:
                if action.isSuccess and not state == ActionBase.ACTION_FAILURE:
                    state = ActionBase.ACTION_SUCCESS
                elif action.isFailure:
                    state = ActionBase.ACTION_FAILURE

                generatedArtefacts.extend(action.outputArtefacts)

        return (state, generatedArtefacts)


    def getFailedActions(self):
        """Returns all actions of the session that have failed."""
        failedActions = []

        with self.lock:
            for action in self._actions:
                # check each action
                if action.isFailure:
                    failedActions.append(action)

        return failedActions


    def getSkippedActions(self):
        """Returns all actions of the session that have been skipped."""
        skippedActions = []

        with self.lock:
            for action in self._actions:
                if action.isSkipped:
                    skippedActions.append(action)

        return skippedActions


    def getSuccessfulActions(self):
        """Returns all actions of the session that have been successful."""
        succActions = []

        with self.lock:
            for action in self._actions:
                if action.isSuccess:
                    succActions.append(action)

        return succActions


    def getSuccessfulActionsWithWarnings(self):
        """Returns all actions of the session that have been successful but with warnings."""
        succActions = []

        with self.lock:
            for action in self._actions:
                if action.isSuccess and len(action.last_warnings) > 0:
                    succActions.append(action)

        return succActions
