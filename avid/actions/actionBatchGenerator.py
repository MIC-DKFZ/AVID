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

from builtins import object
import logging

from avid.linkers import CaseLinker
from avid.selectors import TypeSelector
from avid.sorter import BaseSorter
from avid.splitter import SingleSplitter
import avid.common.artefact.defaultProps as artefactProps
import avid.common.workflow as workflow

logger = logging.getLogger(__name__)

class ActionBatchGenerator(object):
    '''Class helps to generate concrete action instance for a given session and a given set of rules (for selecting, splitting, sorting and linking).
    '''

    PRIMARY_INPUT_KEY = "primaryInput"

    def __init__(self, actionClass, primaryInputSelector, primaryAlias = None, additionalInputSelectors = None,
                 splitter = None, sorter = None, linker = None, dependentLinker = None, session=None,
                 relevanceSelector = None, **actionParameters):
        """init the generator.
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
          @param relevanceSelector: Selector used to specify for all inputs of actions what is relevant. If not set
          it is assumed that only artefact of type TYPE_VALUE_RESULT are relevant.
          @param session: Session object of the workflow the action is working in
        """
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
        leftNames = list(self._dependentLinker.keys())

        while len(leftNames)>0:
            masterName = None
            successfull = False
            for leftName in leftNames:
                masterName = self._dependentLinker[leftName][0]
                if masterName in result:
                    result.append(leftName)
                    leftNames.remove(leftName)
                    successfull = True
                    break
            if not successfull:
                raise RuntimeError('Error in dependent linker definition. Seems to be invald or containes cyclic dependencies. Left dependencies: {}'.format(leftNames))
        return result

    def generateActions(self):
        ''' Method that generates all actions based on the given state of the session and configuration of self.
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
                secondSelections = additionalInputs[additionalKey]
                if secondSelections is None:
                    secondSelections= []
                linkedAdditionals[additionalKey] = self._linker[additionalKey].getLinkedSelection(pos, primaryInput,
                                                                              secondSelections)
            actions.extend(self._generateActions_recursive({self._primaryAlias: primarySplit}, None, linkedAdditionals.copy(), depSequence))

        return actions

    def _generateActions_recursive(self, relevantAdditionalInputs, relevantAdditionalInputPos, additionalInputs, leftInputNames):
        actions = list()
        if relevantAdditionalInputPos is None:
            relevantAdditionalInputPos = dict()

        if leftInputNames is None or len(leftInputNames) == 0:
            singleActionParameters = {**self._singleActionParameters, **relevantAdditionalInputs}
            action = self._actionClass(**singleActionParameters)
            actions.append(action)
        else:
            currentName = leftInputNames[0]
            currentInputs = additionalInputs[currentName]

            newLeftNames = leftInputNames[1:]
            newRelInputs = relevantAdditionalInputs.copy()
            newRelPos = relevantAdditionalInputPos.copy()
            newAdditionalInputs = additionalInputs.copy()

            if currentName in self._dependentLinker:
                sourceName = self._dependentLinker[currentName][0]
                linker = self._dependentLinker[currentName][1]
                currentInputs = list()
                if relevantAdditionalInputPos[sourceName] is not None:
                    currentInput = linker.getLinkedSelection(relevantAdditionalInputPos[sourceName], additionalInputs[sourceName], currentInputs)
                    if currentInputs is None:
                        currentInput = list()
                newAdditionalInputs[currentName] = currentInputs

            if len(currentInputs) == 0:
                newRelPos[currentName] = None
                newRelInputs[currentName] = list()
                actions.extend(self._generateActions_recursive(newRelInputs, newRelPos, newAdditionalInputs, newLeftNames))
            else:
                for (pos,aSplit) in enumerate(currentInputs):
                    newRelPos[currentName] = pos
                    newRelInputs[currentName] = aSplit
                    actions.extend(self._generateActions_recursive(newRelInputs, newRelPos, newAdditionalInputs, newLeftNames))

        return actions
