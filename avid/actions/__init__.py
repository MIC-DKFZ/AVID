# AVID
# Automated workflow system for cohort analysis in radiology and radiation therapy
#
# Copyright (c) German Cancer Research Center,
# Software development for Integrated Diagnostic and Therapy (SIDT).
# All rights reserved.
#
# This software is distributed WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.
#
# See LICENSE.txt or http://www.dkfz.de/en/sidt/index.html for details.

from builtins import str
from builtins import object
import os
import logging
import time
import uuid

from avid.linkers import CaseLinker
from avid.selectors import TypeSelector
from avid.sorter import BaseSorter
from avid.splitter import SingleSplitter
from ..common import actionToken
from ..common.artefact.generator import generateArtefactEntry
import avid.common.artefact.generator as artefactGenerator
import avid.common.artefact as artefactHelper
import avid.common.artefact.defaultProps as artefactProps
from .simpleScheduler import SimpleScheduler
import avid.common.workflow as workflow
import avid.selectors as selectors

logger = logging.getLogger(__name__)


class ActionBase(object):
    '''Base class for action objects used in the pipeline.'''

    def __init__(self, actionTag, session=None, additionalActionProps=None):
        '''init the action and setting the workflow session, the action is working
          in.
          @param session: Session object of the workflow the action is working in
          @param actionTag: Tag of the action within the session
          @param additionalActionProps: Dictionary that can be used to define additional
          properties that should be added to any artefact that are produced by the action.
        '''

        self._instanceUID = uuid.uuid4()
        if session is None:
            # check if we have a current generated global session we can use
            if workflow.currentGeneratedSession is not None:
                self._session = workflow.currentGeneratedSession
            else:
                raise ValueError("Session passed to the action is invalid. Session is None.")
        else:
            self._session = session

        self._actionTag = actionTag

        self._additionalActionProps = additionalActionProps
        if self._additionalActionProps is None:
            self._additionalActionProps = {}

        self._outputArtefacts = list()

    @property
    def actionTag(self):
        return self._actionTag

    @property
    def actionInstanceUID(self):
        return str(self._instanceUID)

    @property
    def outputArtefacts(self):
        return self.indicateOutputs()

    def indicateOutputs(self):
        ''' Return a list of artefact entries the action will produce if do() is
          called. The method should return complete entries.
          Therefore the entries should already contain the url where they
          *will* be stored if the action is executed.'''
        if len(self._outputArtefacts) is 0:
            self._outputArtefacts = self._indicateOutputs()

        return self._outputArtefacts

    def _indicateOutputs(self):
        ''' Internl function that is called by indicate outputs if no output artefact
          list exists yet. Return a list of artefact entries the action will produce
          if do() is called. The method should
          return complete entries. Therefore the enties should already contain the
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
        # Implement: return a list of valid artefact entries
        pass

    def _do(self):
        ''' Internal function that triggers the processing of an action.
          This Method is used internally (e.g. when ever an action is used by an other
          action; and no action tag should be added to the session. '''
        raise NotImplementedError("Reimplement in a derived class to function correctly.")
        # Implement: what the action should realy do
        pass

    def do(self, autoTokenAdding=True):
        '''Triggers the processing of an action. This should be used as public
        trigger of an action.
        @param autoTokenAdding You can control if the resulting session token should
        be automatically added to the session by the optional flag autoTokenAdding.
        Normally it is activated, but may be useful to deactivate it if you trigger
        an action within an other action. See the schedulers of batch actions for
        example.'''
        global logger
        logger.info("Starting action: " + self.instanceName + " (UID: " + self.actionInstanceUID + ") ...")

        token = self._do()

        if autoTokenAdding:
            self._session.addActionToken(token)

        status = "SUCCESS"
        if token.isSkipped():
            status = "SKIPPED"
        elif token.isFailure():
            status = "FAILURE"
        logger.info("Finished action: " + self.instanceName + " (UID: " + self.actionInstanceUID + ") -> " + status)
        return token

    def generateActionToken(self, state=actionToken.ACTION_SUCCESS):
        ''' Helper function that creates a action token (with the passed state
        for the current action instance and pass the token back. '''
        token = actionToken.ActionToken(self._session, self.actionTag, self.instanceName, state)

        return token


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
        ActionBase.__init__(self, actionTag, session, additionalActionProps)

        self._alwaysDo = alwaysDo
        # CaseInstance that should all artefacts generated by this action have
        self._caseInstance = None

        self._inputArtefacts = dict()

        self._propInheritanceDict = propInheritanceDict
        if self._propInheritanceDict is None:
            self._propInheritanceDict = dict()

    def _addInputArtefacts(self, **inputs):
        '''This function should be used in the init of derived actions to register
        artefacts as input artefact for the action instance. This will be used for several
        things; e.g. determining the Caseinstance of the action instance, used in the
        generation of new artefacts, used to determine if outputs can be generated.'''
        for iKey in inputs:
            if inputs[iKey] is not None:
                self._inputArtefacts[iKey] = inputs[iKey]

        self._setCaseInstanceByArtefact(list(self._inputArtefacts.values()))

    def _setCaseInstanceByArtefact(self, *inputArtefacts):
        '''defines the case instance used by the action based on the passed input artefact.'''
        stubArtefact = dict()
        stubArtefact[artefactProps.CASEINSTANCE] = None
        if not artefactHelper.ensureCaseInstanceValidity(stubArtefact, *inputArtefacts):
            logger.warning("Case instance conflict raised by the input artefact of the action. Input artefacts %s",
                           inputArtefacts)

        self._caseInstance = stubArtefact[artefactProps.CASEINSTANCE]

    def generateArtefact(self, reference=None, copyAdditionalPropsFromReference=True, userDefinedProps = None, urlHumanPrefix = None, urlExtension = None):
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
        @param reference An other artefact as reference. If given, the following
        properties will be copied to the new artefact: Case, case instance, timepoint,
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
                    if propID in self._inputArtefacts[self._propInheritanceDict[propID]]:
                        result[propID] = artefactHelper.getArtefactProperty(self._inputArtefacts[self._propInheritanceDict[propID]],propID)
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
          inputs[inputName] = artefactHelper.getArtefactProperty(self._inputArtefacts[inputName],artefactProps.ID)
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

    def _checkOutputs(self, outputs):
        '''Checks if the given artefacts exists as file. Outputs that do not exist
          are marked as invalid.
          @return a tupple as result. 1. indicating if all outputs are valid. 2. the
          output list with updated validity state.'''
        valid = True
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

    def _getInvalidInputs(self):
        '''Helper function that checks if registered inputs for the action are invalid.
          @return Returns a dict with all invalid inputs. An empty indicates that all inputs are valid.'''

        invalidInputs = dict()

        for key in self._inputArtefacts:
            if not self._inputArtefacts[key] is None and self._inputArtefacts[key].is_invalid():
                invalidInputs[key] = self._inputArtefacts[key]

        return invalidInputs

    def _do(self):
        ''' Triggers the processing of an action. '''
        global logger

        outputs = self.indicateOutputs()
        (isNeeded, alternatives) = self._checkNecessity(outputs)

        token = self.generateActionToken()

        if self._alwaysDo or isNeeded:
            isValid = False
      
            starttime = time.time()
            endtime = None
            
            invalidInputs = self._getInvalidInputs()
            if len(invalidInputs) is 0:

                try:
                    self._generateOutputs()
                    endtime = time.time()
                    (isValid, outputs) = self._checkOutputs(outputs)
                except BaseException as e:
                    logger.warning(
                        '(Action instance UID: %s) Error while generating outputs for action tag "%s". All outputs will be marked as invalid. Error details: %s',
                        self.actionInstanceUID, self.actionTag, str(e))
                except:
                    logger.warning(
                        '(Action instance UID: %s) Unkown error while generating outputs for action tag "%s". All outputs will be marked as invalid.',
                        self.actionInstanceUID, self.actionTag)
            else:
                logger.warning("Action failed due to at least one invalid input. All outputs are marked as invalid. Invalid inputs: %s", str(self._inputArtefacts))

            if not isValid:
                for artefact in outputs:
                    artefact[artefactProps.INVALID] = True

            token.generatedArtefacts = outputs
      
            for artefact in outputs:
                try:
                    artefact[artefactProps.EXECUTION_DURATION] = endtime - starttime
                except:
                    pass
        
                self._session.addArtefact(artefact, True)

            if not isValid:
                token.state = actionToken.ACTION_FAILUER

        else:
            token.generatedArtefacts = alternatives
            token.state = actionToken.ACTION_SKIPPED

        return token


class BatchActionBase(ActionBase):
    '''Base class for action objects that are used together with selectors and
      should therefore able to process a batch of SingleActionBased actions.'''

    def __init__(self, actionTag, alwaysDo=False, scheduler=SimpleScheduler(), session=None,
                 additionalActionProps=None):
        '''init the action and setting the workflow session, the action is working
          in.
          @param session: Session object of the workflow the action is working in
          @param actionTag: Tag of the action within the session
          @param alwaysDo: Indicates if single actions should generate its artefacts even
          if they already exist in the workflow (True) or if the action should skip
          the processing (False).
          @param scheduler Strategy how to execute the single actions.
        '''
        ActionBase.__init__(self, actionTag, session, additionalActionProps)

        self._alwaysDo = alwaysDo
        self._actions = None
        self._scheduler = scheduler  # scheduler that should be used to execute the jobs

    def ensureRelevantArtefacts(self, artefacts, relevantSelector, infoTag="none"):
        ''' Helper function that filters the passed artefact list by the passed relevantSelector.
        Returns the list containing the relevant artefacts. If the valid list is empty
        it will be logged as. This function is for batch actions that want to ensure specific
        properties for there artefact before they are used in the batch processing (e.g. only
        artefacts of type "result" are allowed).'''

        result = relevantSelector.getSelection(artefacts)

        if len(result) == 0:
            global logger
            logger.debug("Input selection contains no valid artefacts. Info tag: %s", infoTag)

        return result

    def _generateName(self):
        return self.__class__.__name__ + "_" + str(self.actionTag)

    def _indicateOutputs(self):
        ''' Return a list of artefact entries the action will produce if do() is
          called. Reimplement this method for derived actions. The method should
          return complete entries. Therefore the enties should already contain the
          url where they *will* be stored if the action is executed.'''
        if self._actions is None:
            self._actions = self._generateActions()

        outputs = list()

        for action in self._actions:
            outputs += action.indicateOutputs()

        return outputs

    def _generateActions(self):
        ''' Internal method that should generate all single actions that should be
          executed and returns them in a list. This method should be
          reimplemented in derived classes to do the real work of dispatching the
          selectors and creating the action functors for all needed actions.
          @postcondition: all needed single actions are created and configured to be
          read to be executed.'''
        raise NotImplementedError("Reimplement in a derived class to function correctly.")
        # Implement: generat all jobs and return them.
        pass

    def _do(self):
        ''' Triggers the processing of an action. '''

        if self._actions is None:
            self._actions = self._generateActions()

        tokens = self._scheduler.execute(self._actions)

        token = self.generateActionToken(actionToken.ACTION_SKIPPED)

        for aToken in tokens:
            if aToken.isSuccess() and not token.isFailure():
                token.state = actionToken.ACTION_SUCCESS
            elif aToken.isFailure():
                token.state = actionToken.ACTION_FAILUER

            token.generatedArtefacts.extend(aToken.generatedArtefacts)

        return token


class BatchActionBase(ActionBase):
    '''Base class for action objects that are used together with selectors and
      should therefore able to process a batch of SingleActionBased actions.'''

    def __init__(self, actionTag, alwaysDo=False, scheduler=SimpleScheduler(), session=None,
                 additionalActionProps=None):
        '''init the action and setting the workflow session, the action is working
          in.
          @param session: Session object of the workflow the action is working in
          @param actionTag: Tag of the action within the session
          @param alwaysDo: Indicates if single actions should generate its artefacts even
          if they already exist in the workflow (True) or if the action should skip
          the processing (False).
          @param scheduler Strategy how to execute the single actions.
        '''
        ActionBase.__init__(self, actionTag, session, additionalActionProps)

        self._alwaysDo = alwaysDo
        self._actions = None
        self._scheduler = scheduler  # scheduler that should be used to execute the jobs

    def ensureRelevantArtefacts(self, artefacts, relevantSelector, infoTag="none"):
        ''' Helper function that filters the passed artefact list by the passed relevantSelector.
        Returns the list containing the relevant artefacts. If the valid list is empty
        it will be logged as. This function is for batch actions that want to ensure specific
        properties for there artefact before they are used in the batch processing (e.g. only
        artefacts of type "result" are allowed).'''

        result = relevantSelector.getSelection(artefacts)

        if len(result) == 0:
            global logger
            logger.debug("Input selection contains no valid artefacts. Info tag: %s", infoTag)

        return result

    def _generateName(self):
        return self.__class__.__name__ + "_" + str(self.actionTag)

    def _indicateOutputs(self):
        ''' Return a list of artefact entries the action will produce if do() is
          called. Reimplement this method for derived actions. The method should
          return complete entries. Therefore the enties should already contain the
          url where they *will* be stored if the action is executed.'''
        if self._actions is None:
            self._actions = self._generateActions()

        outputs = list()

        for action in self._actions:
            outputs += action.indicateOutputs()

        return outputs

    def _generateActions(self):
        ''' Internal method that should generate all single actions that should be
          executed and returns them in a list. This method should be
          reimplemented in derived classes to do the real work of dispatching the
          selectors and creating the action functors for all needed actions.
          @postcondition: all needed single actions are created and configured to be
          read to be executed.'''
        raise NotImplementedError("Reimplement in a derived class to function correctly.")
        # Implement: generat all jobs and return them.
        pass

    def _do(self):
        ''' Triggers the processing of an action. '''

        if self._actions is None:
            self._actions = self._generateActions()

        tokens = self._scheduler.execute(self._actions)

        token = self.generateActionToken(actionToken.ACTION_SKIPPED)

        for aToken in tokens:
            if aToken.isSuccess() and not token.isFailure():
                token.state = actionToken.ACTION_SUCCESS
            elif aToken.isFailure():
                token.state = actionToken.ACTION_FAILUER

            token.generatedArtefacts.extend(aToken.generatedArtefacts)

        return token


class ActionBatchGenerator(object):
    '''Class helps to generate concrete action instance for a given session and a given set of rules (for selecting, splitting, sorting and linking).
    '''

    PRIMARY_INPUT_KEY = "primaryInput"

    def __init__(self, actionClass, primaryInputSelector, primaryAlias = None, additionalInputSelectors = None,
                 splitter = None, sorter = None, linker = None, dependentLinker = None, session=None,
                 relevanceSelector = None, **actionParameters):
        '''init the generator.
          @param actionClass: Class of the action that should be generated
          @param primaryInputSelector: Selector that indicates the primary input for the actions that should be generated
          @param primaryAlias: Name of the primary input that should be used as argument key if passed to action.
          If not set PRIMARY_INPUT_KEY will be used.
          @param additionalInputSelectors: Dictionary containing additional input selectors for other inputs that should
          be passed to an action instance. Key is the name of an additional input an also the argument name used to pass
          the input to the action instance. The associated dict value must be a selector instance or None to indicate
          that this input will have no data but exists.
          @param splitter: Dictionary specifying a splitter that should be used for a specific input (primary or additional)
          If no splitter is defined explicitly for an input SingleSplitter() will be assumed. The key indicates the
          input that should be associated with the splitter. To associate primary input use PRIMARY_INPUT_KEY as key.The
          values of the dict are the splitter instances that should be used for the respective key.
          @param sorter: Dictionary specifying a sorter that should be used for a specific input (primary or additional)
          If no sorter is defined explicitly for an input BaseSorter() (so no sorting at all) will be assumed.
          The key indicates the input that should be associated with the sorter. To associate primary input use
          PRIMARY_INPUT_KEY as key. The values of the dict are the sorter instances that should be used for the
          respective key.
          @param linker: Dictionary specifying a linker that should be used for a specific additional input
          to link it with the primary input. Thus the master selection passed to the linker will always be provided by
          the primary input.
          If no linker is defined explicitly for an input CaseLinker() (so all inputs must have the same case) will be
          assumed. The key indicates the input that should be associated with the linker. The values of the dict are the
          linker instances that should be used for the respective key.
          @param dependentLinker: Allows to specify linkage for an additional input where the master selection must not
          be the primary input (in contrast to using the linker argument). Thus you can specifies that an additional
          input A is (also) linked to an additional input B. The method assumes the following structure of the variable.
          It is a dictionary. The dictionary key indicates the input that should be linked. So it can be any additional
          input. It must not be the primary input. The value associated with a dict key is an iterable (e.g. list) the
          first element is the name of the input that serves as master for the linkage. It may be any additional input
          (except itself = key of the value) or the primary input. The second element is the linker instance that should
          be used. You may combine linker and dependentLinker specifications for any additional input.
          To associate primary input as master use PRIMARY_INPUT_KEY as value.
          @param relevanceSelector: Selector used to specify for all inputs an actions what is relevant. If not set
          it is assumed that only artefact of type TYPE_VALUE_RESULT are relevant.
          @param session: Session object of the workflow the action is working in
        '''
        if session is None:
            # check if we have a current generated global session we can use
            if workflow.currentGeneratedSession is not None:
                self._session = workflow.currentGeneratedSession
            else:
                raise ValueError("Session passed to the action is invalid. Session is None.")
        else:
            self._session = session

        self._actionClass = actionClass

        self._singleActionParameters = actionParameters

        self._primaryInputSelector = primaryInputSelector

        self._primaryAlias = primaryAlias
        if self._primaryAlias is None:
            self._primaryAlias = self.PRIMARY_INPUT_KEY

        self._additionalInputSelectors = additionalInputSelectors
        if self._additionalInputSelectors is None:
            self._additionalInputSelectors = dict()

        if self.PRIMARY_INPUT_KEY in self._additionalInputSelectors:
            raise ValueError('Additional input selectors passed to the action are invalid. It does contain key value "'+self.PRIMARY_INPUT_KEY+'" reserved for the primary input channel. Check passed additional input dictionary %s.'.format(self._additionalInputSelectors))

        self._splitter = dict()
        if splitter is not None:
            self._splitter = splitter.copy()
        for key in self._additionalInputSelectors:
            if not key in self._splitter:
                self._splitter[key] = SingleSplitter()
        if not self.PRIMARY_INPUT_KEY in self._splitter:
            self._splitter["primaryInput"] = SingleSplitter()

        self._sorter = dict()
        if sorter is not None:
            self._sorter = sorter.copy()
        for key in self._additionalInputSelectors:
            if not key in self._sorter:
                self._sorter[key] = BaseSorter()

        if not self.PRIMARY_INPUT_KEY in self._sorter:
            self._sorter["primaryInput"] = BaseSorter()

        self._linker = dict()
        if linker is not None:
            self._linker = linker.copy()
        if self.PRIMARY_INPUT_KEY in self._linker:
            raise ValueError('Primary input can not have a linkage. Invalid linker setting. Check passed dictionary %s.'.format(self._dependentLinker))

        for key in self._additionalInputSelectors:
            if not key in self._linker:
                self._linker[key] = CaseLinker()

        self._dependentLinker = dict()
        if dependentLinker is not None:
            self._dependentLinker = dependentLinker.copy()
        if self.PRIMARY_INPUT_KEY in self._dependentLinker:
            raise ValueError('Primary input can not have a linkage. Invalid dependentLinker setting. Check passed dictionary %s.'.format(self._dependentLinker))

        for key in self._dependentLinker:
            if self._dependentLinker[key][0] is key:
                raise ValueError('Recursive linkage dependency. Input indicates to depend on itself. Check passed dependentLinker dictionary %s.'.format(
                        self._dependentLinker))

        self._relevanceSelector = relevanceSelector
        if self._relevanceSelector is None:
            self._relevanceSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)


    def _ensureRelevantArtefacts(self, artefacts, infoTag="none"):
        ''' Helper function that filters the passed artefact list by the passed relevantSelector.
        Returns the list containing the relevant artefacts. If the valid list is empty
        it will be logged as. This function is for batch actions that want to ensure specific
        properties for there artefact before they are used in the batch processing (e.g. only
        artefacts of type "result" are allowed).'''

        result = self._relevanceSelector.getSelection(artefacts)

        if len(result) == 0:
            global logger
            logger.debug("Input selection contains no valid artefacts. Info tag: %s", infoTag)

        return result

    def _prepareInputArtifacts(self, inputName):
        '''Gets, for one input all artefact form the session, sorts and splits them.'''
        artefacts = None

        selector = self._primaryInputSelector
        if not inputName == self.PRIMARY_INPUT_KEY:
            selector = self._additionalInputSelectors[inputName]

        if selector is not None:
            artefacts = selector.getSelection(self._session.artefacts)
            artefacts = self._ensureRelevantArtefacts(artefacts, inputName)

            splittedArtefacts = self._splitter[inputName].splitSelection(artefacts)

            sortedArtefacts = list()
            for split in splittedArtefacts:
                sortedArtefacts.append(self._sorter[inputName].sortSelection(split))

            artefacts = sortedArtefacts

        return artefacts

    def _generateDependencySequence(self):
        names = self._additionalInputSelectors.keys()
        #Get all inputs that do not depend on others and put it directly in the list
        result = [name for name in names if name not in self._dependentLinker]
        leftNames = self._dependentLinker.keys()

        while len(leftNames)>0:
            masterName = None
            for leftName in leftNames:
                masterName = self._dependentLinker[leftName][0]
                if masterName in result:
                    result.append(leftName)
                    leftNames.remove(leftName)
                    break
            raise RuntimeError('Error in dependent linker definition. Seems to be invald or containes cyclic dependencies. Left dependencies: {}'.format(leftNames))
        return result

    def generateActions(self):
        ''' Method that generates all actions based on the given state of the session and configuration nof self.
          For the strategy how the actions are generated see the explination in the class documentation.'''

        primaryInput = self._prepareInputArtifacts(inputName=self.PRIMARY_INPUT_KEY)

        additionalInputs = dict()
        for key in self._additionalInputSelectors:
            additionalInputs[key] = self._prepareInputArtifacts(inputName=key)

        actions = list()
        depSequence = self._generateDependencySequence()

        for (pos, primarySplit) in enumerate(primaryInput):
            linkedAdditionals = dict()
            for additionalKey in additionalInputs:
                linkedAdditionals[additionalKey] = self._linker[additionalKey].getLinkedSelection(pos, primaryInput,
                                                                              additionalInputs[additionalKey])
            actions.extend(self._generateActions_recursive({self._primaryAlias: primarySplit}, None, linkedAdditionals.copy(), depSequence))

        return actions

    def _generateActions_recursive(self, relevantAdditionalInputs, relevantAddtitionalInputPos, additionalInputs, leftInputNames):
        actions = list()
        if relevantAddtitionalInputPos is None:
            relevantAddtitionalInputPos = dict()

        if leftInputNames is None or len(leftInputNames) == 0:
            singleActionParameters = {**self._singleActionParameters, **relevantAdditionalInputs}
            action = self._actionClass(**singleActionParameters)
            actions.append(action)
        else:
            currentName = leftInputNames[0]
            currentInputs = additionalInputs[currentName]

            newLeftNames = leftInputNames[1:]
            newRelInputs = relevantAdditionalInputs.copy()
            newRelPos = relevantAddtitionalInputPos.copy()
            newAdditionalInputs = additionalInputs.copy()

            if currentName in self._dependentLinker:
                sourceName = self._dependentLinker[currentName][0]
                linker = self._dependentLinker[currentName][1]
                currentInputs = linker.getLinkedSelection(relevantAddtitionalInputPos[sourceName], additionalInputs[sourceName], currentInputs)
                newAdditionalInputs[currentName] = currentInputs

            for (pos,aSplit) in enumerate(currentInputs):
                newRelPos[currentName] = pos
                newRelInputs[currentName] = aSplit
                actions.extend(self._generateActions_recursive(newRelInputs, newRelPos, newAdditionalInputs, newLeftNames))

        return actions
