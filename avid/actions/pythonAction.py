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
import avid.common.demultiplexer as demux

logger = logging.getLogger(__name__)

class PythonAction(SingleActionBase):
  '''Action that offers a generic wrapper arround any python callable. The basic idea is to have a simple possibility
   to define action that execute a python script. The python script that should be executed must be passed as callable.
   The action will call the callable with the following arguments:
   1. all unknown keyword arguments that are passed to the action (scriptArgs).
   2. an argument called outputs, that contain the result of self.indicateOutputs.
   For the arguments the user of the action is free to use any keyword that is not reserved by the action and is not
   "outputs". Additionally the action assumes that all unknown keyword arguments that start with "inputs" are lists of
   artefacts that serves as input.
   @param generateCallable A callable that will be called to generat the outputs. The action assumes that all outputs
   are generated an stored at their designated location.
   @param indicateCallable A callable that, if defined, will be called (like generateCallable) to query the outputs.
   The action assumes that the callable returns a list of output artefacts (like self.indicateOutputs). If this callable
   is not set, the default is one output that will be defined by the action and uses the first input artefact as reference.
   The signature of indicateCallable is: indicateCallable(actionInstance ( = Instance of the calling action), **allArgs
    (= all arguments passed to the action)
   @param passOnlyURLs If set to true only URLs of the artefacts, instead of the artefacts themself, will be passed to
    generateCallable.
   @scriptedParameters Every unkown parameters that will be passed to generateCallable.
   @defaultoutputextension Output extension that should be used if no indicateCallable is defined.'''

  def __init__(self, generateCallable, indicateCallable = None, passOnlyURLs = True, defaultoutputextension = 'nrrd',actionTag="Python", alwaysDo=True, session=None, additionalActionProps=None,
               propInheritanceDict = None, **scriptArgs):
    SingleActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps, propInheritanceDict = propInheritanceDict)
    self._generateCallable = generateCallable
    self._indicateCallable = indicateCallable
    self._passOnlyURLs = passOnlyURLs
    self._outputextension = defaultoutputextension

    self._inputArgs = dict()
    self._args = dict()

    for name in scriptArgs:
        if name.startswith('inputs'):
            self._inputArgs[name] = scriptArgs[name]
        else:
            self._args[name] = scriptArgs[name]

    tempInput = dict()
    for name in self._inputArgs:
        if isinstance(self._inputArgs[name], artefactHelper.Artefact):
            tempInput[name] = self._inputArgs[name]
        else:
            #assuming a list of artefacts
            for pos, artefact in enumerate(self._inputArgs[name]):
                tempInput['{}_{}'.format(name,pos)]= artefact

    self._addInputArtefacts(**tempInput)

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

  def indicateOutputs(self):
      allargs = self._inputArgs.copy()
      allargs.update(self._args)
      if self._indicateCallable is not None:
          self._resultArtefacts = self._indicateCallable(actionInstance = self, **allargs)
          #check if its realy a list of artefacts
          try:
              for artifact in self._resultArtefacts:
                  if not isinstance(artifact, artefactHelper.Artefact):
                      raise TypeError('Indicate callable does not return a list of artefacts. Please check callable. Erroneous return: {}'.format(self._resultArtefacts))
          except:
              raise TypeError(
                  'Indicate callable does not return a list of artefacts. Please check callable. Erroneous return: {}'.format(
                      self._resultArtefacts))

      else:
          #we generate the default as template the first input in the dictionary
          self._resultArtefacts = [self.generateArtefact(self._inputArtefacts[sorted(self._inputArtefacts.keys())[0]],
                                                         userDefinedProps={artefactProps.TYPE:artefactProps.TYPE_VALUE_RESULT},
                                                         urlHumanPrefix=self.instanceName,
                                                         urlExtension=self._outputextension)]
      return self._resultArtefacts

  def _generateOutputs(self):
    allargs = self._args.copy()

    outputs = list()
    for output in self._resultArtefacts:
        if self._passOnlyURLs:
            outputs.append(artefactHelper.getArtefactProperty(output, artefactProps.URL))
        else:
            outputs.append(output)

    allargs['outputs'] = outputs

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

    destPath = artefactHelper.getArtefactProperty(self._resultArtefacts[0], artefactProps.URL)
    checkAndCreateDir(os.path.dirname(destPath))
    self._generateCallable(**allargs)


class PythonUnaryBatchAction(BatchActionBase):
  '''Batch class that assumes only one input artefact that will be passed to the script.'''

  def __init__(self, inputSelector, actionTag="UnaryScript", alwaysDo=False,
               session=None, additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._inputs = inputSelector.getSelection(self._session.artefacts)

    self._singleActionParameters = singleActionParameters

  def _generateActions(self):
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)
    inputs = self.ensureRelevantArtefacts(self._inputs, resultSelector, "input")

    actions = list()

    for input in inputs:
      action = PythonAction(inputs = [input], actionTag = self._actionTag, alwaysDo=self._alwaysDo,
                             session=self._session,
                             additionalActionProps=self._additionalActionProps,
                             **self._singleActionParameters)
      actions.append(action)

    return actions


class PythonBinaryBatchAction(BatchActionBase):
  '''Batch class that assumes two input artefacts (joined by an (optional) linker) will be passed to the script.
     The batch class assumes that the python script takes the inputs as arguments "inputs1" and "inputs2".'''

  def __init__(self, inputs1Selector, inputs2Selector, inputLinker = None, actionTag="BinaryScript", alwaysDo=False,
               session=None, additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._inputs1 = inputs1Selector.getSelection(self._session.artefacts)
    self._inputs2 = inputs2Selector.getSelection(self._session.artefacts)

    self._inputLinker = inputLinker
    if inputLinker is None:
        self._inputLinker = CaseLinker()

    self._singleActionParameters = singleActionParameters

  def _generateActions(self):
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)

    inputs1 = self.ensureRelevantArtefacts(self._inputs1, resultSelector, "1st input")
    inputs2 = self.ensureRelevantArtefacts(self._inputs2, resultSelector, "1st input")

    actions = list()

    for (pos, input1) in enumerate(inputs1):
        linked2 = self._inputLinker.getLinkedSelection(masterIndex=pos, masterSelection=inputs1, slaveSelection=inputs2)

        for lt in linked2:
            action = PythonAction(inputs1=[input1], inputs2=[lt], actionTag=self._actionTag, alwaysDo=self._alwaysDo,
                                  session=self._session,
                                  additionalActionProps=self._additionalActionProps,
                                  **self._singleActionParameters)
            actions.append(action)

    return actions


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
     - all other inputs with the name they where passed to the batch action.'''

  def __init__(self, inputsMaster, actionTag="NaryScript", alwaysDo=False,
               session=None, additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
    BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

    self._inputsMaster = inputsMaster.getSelection(self._session.artefacts)
    self._otherInputs = dict()
    self._singleActionParameters = dict()
    self._otherLinker = dict()
    for paramName in singleActionParameters:
        if paramName.startswith('inputs'):
            if paramName.endswith('Linker'):
                self._otherLinker[paramName[:-6]] = singleActionParameters[paramName]
            else:
                self._otherInputs[paramName] = singleActionParameters[paramName].getSelection(self._session.artefacts)
        else:
            self._singleActionParameters[paramName] = singleActionParameters[paramName]

    for inputName in self._otherInputs:
        if not inputName in self._otherLinker:
            self._otherLinker[inputName] = CaseLinker()+CaseInstanceLinker()

  def _generateActions_recursive(self, relevantAdditionalInputs, additionalInputs, leftInputNames):
    actions = list()
    if leftInputNames is None or len(leftInputNames)==0:
        singleActionParameters = {**self._singleActionParameters, **relevantAdditionalInputs}
        action = PythonAction(actionTag=self._actionTag, alwaysDo=self._alwaysDo, session=self._session,
                            additionalActionProps=self._additionalActionProps, **singleActionParameters)
        actions.append(action)
    else:
        currentName = leftInputNames[0]
        currentInputs = additionalInputs[currentName]
        newLeftNames = leftInputNames[1:]
        newRelInputs = relevantAdditionalInputs.copy()
        for anInput in currentInputs:
            newRelInputs[currentName] = [anInput]
            actions.extend(self._generateActions_recursive(newRelInputs, additionalInputs, newLeftNames))

    return actions

  def _generateActions(self):
    resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)

    inputsMaster = self.ensureRelevantArtefacts(self._inputsMaster, resultSelector, "master input")
    otherInputs = dict()
    for inputName in self._otherInputs:
        otherInputs[inputName] = self.ensureRelevantArtefacts(self._otherInputs[inputName], resultSelector, inputName)

    actions = list()

    for (pos, inputMaster) in enumerate(inputsMaster):
        linkedOthers = dict()
        for otherInputName in otherInputs:
            linked = self._otherLinker[otherInputName].getLinkedSelection(pos, inputsMaster, self._otherInputs[otherInputName])
            linkedOthers[otherInputName] = linked
        actions.extend(self._generateActions_recursive({'inputsMaster':[inputMaster]}, linkedOthers, sorted(linkedOthers.keys())))

    return actions


class PythonUnaryStackBatchAction(BatchActionBase):
    '''Batch class that assumes a list of input artefacts will be passed to the script.
    The list of artefacts is defined via the input selector.
    @param splitProperties You can define a list of split properties (list of property names)
    to separate it into different actions (e.g. like the PixelDumpMiniApp action.
    '''

    def __init__(self, inputSelector, splitProperties = None, actionTag="UnaryStackScript", alwaysDo=False,
               session=None, additionalActionProps=None, scheduler=SimpleScheduler(), **singleActionParameters):
      BatchActionBase.__init__(self, actionTag, alwaysDo, scheduler, session, additionalActionProps)

      self._inputs = inputSelector.getSelection(self._session.artefacts)
      self._splitProps = splitProperties

      self._singleActionParameters = singleActionParameters


    def _generateActions(self):
      resultSelector = TypeSelector(artefactProps.TYPE_VALUE_RESULT)
      allinputs = self.ensureRelevantArtefacts(self._inputs, resultSelector, "inputs")

      global logger

      splittedInputs = [allinputs]

      if self._splitProps is not None:
          splittedInputs = demux.splitArtefact(allinputs, *self._splitProps)

      actions = list()

      for inputs in splittedInputs:
          action = PythonAction(inputs=inputs, actionTag=self._actionTag, alwaysDo=self._alwaysDo,
                                          session=self._session,
                                          additionalActionProps=self._additionalActionProps,
                                          **self._singleActionParameters)
          actions.append(action)
      return actions