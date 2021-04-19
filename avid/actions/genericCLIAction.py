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

import os
import logging

import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper

from avid.common import osChecker, AVIDUrlLocater

from .cliActionBase import CLIActionBase

logger = logging.getLogger(__name__)


def _generateFlag(flagName):
    if len(flagName) == 1:
        return '-{}'.format(flagName)
    else:
        return '--{}'.format(flagName)

def generate_cli_call(exec_url, artefact_args, cli_args=None, arg_positions=None):
    '''Helper that generates the the cli call string for a given set of artefact selection arguments and normal
     arguments.
     :param exec_url: The argument for the cli itself.
     :param artefact_args: Dictionary of artefact selections as values. The key is the flag (without "-" or "--"; they will be
      added outamatically depending on the size of the key; one character keys will completed with "-", others with
      "--"). If the selection contains more then one artefact all artefact urls will be added as single arguments after
      the flag.
     :param cliArgs: Dictionary with all arguments (except the artefact inputs and outputs) that should be passed to
      the cli. The key is the argument/flag name (without "-" or "--"; they will be
      added outamatically depending on the size of the key; one character keys will completed with "-", others with
      "--"). If the value is not None it will be also added after the argument.
     :param arg_positions list that contains the keys of all arguments (from artefact_args and cli_args) that
      are not flag based but positional arguments. Those arguments will be added in the order of the list before the
      positional arguments.
      '''
    content = '"{}"'.format(exec_url)
    if arg_positions is None:
        arg_positions = list()

    for key in arg_positions:
        if key in artefact_args:
            for artefact in artefact_args[key]:
                artefactPath = artefactHelper.getArtefactProperty(artefact, artefactProps.URL)
                if artefactPath is not None:
                    content += ' "{}"'.format(artefactPath)
        elif cli_args is not None and key in cli_args:
            content += ' "{}"'.format(cli_args[key])

    for pos, artefactKey in enumerate(artefact_args):
        if not artefactKey in arg_positions and artefact_args[artefactKey] is not None:
            artefact_content = ''
            for artefact in artefact_args[artefactKey]:
                artefactPath = artefactHelper.getArtefactProperty(artefact, artefactProps.URL)
                if artefactPath is not None:
                    artefact_content += ' "{}"'.format(artefactPath)

            if len(artefact_content)>0:
                content += ' {}'.format(_generateFlag(artefactKey))+artefact_content

    if cli_args is not None:
        for argKey in cli_args:
            if not argKey in arg_positions:
                content += ' {}'.format(_generateFlag(argKey))
                if cli_args[argKey] is not None:
                    content += ' "{}"'.format(cli_args[argKey])

    return content


class GenericCLIAction(CLIActionBase):
    '''Action that offers a generic wrapper around a cli execution of an action. The basic idea is to have a simple
     possibility to define an action that execute a CLI executable. All passed artefact selections are directly
     converted into cli arguments. The user can define additional cli arguments and if the arguments are flag based
     or positional arguments. If a user wants to use a tool not known to AVID, the users can specify own actionID and
     configure it with avidconig (system wide) or at runtime for a specific session (setWorkflowActionTool()) to point
     to a certain executable.
     For more details see the documentation of __init_.'''

    def __init__(self, actionID, outputFlags = None, indicateCallable = None, cliArgs= None, illegalArgs=None,
                 argPositions = None, defaultoutputextension = 'nrrd', actionTag="GenericCLI", alwaysDo=False,
                 session=None, additionalActionProps=None, actionConfig=None, propInheritanceDict=None, **inputArgs):
        '''
        :param actionID: actionID that will be used to deduce the tool/executable for this action instance.
        :param outputFlags: The argument/flag name (without "-" or "--"; the will be added outamatically) of the output.
        If set to none, the action assumes that the output parameter are indexed by and directly added in the beginning
        without a flag.
        :param indicateCallable: A callable that, if defined, will be called to query the outputs.
         The action assumes that the callable returns a list of output artefacts (like self.indicateOutputs). If this callable
         is not set, the default is one output that will be defined by the action and uses the first input artefact as reference.
         The signature of indicateCallable is: indicateCallable(actionInstance ( = Instance of the calling action), **allArgs
          (= all arguments passed to the action)
        :param defaultoutputextension: Output extension that should be used if no indicateCallable is defined.
        :param cliArgs: Dictionary with all arguments (except the artefact inputs and outputs) that should be passed to
        the cli. The key is the argument/flag name (without "-" or "--"; the will be added outamatically). If the value is not
        None it will be also added after the argument.
        :param illegalArgs: List that can be used to add additional forbidden argument names, that may not be
        contained in cliArgs.
        :param inputArgs: It is assumed that all unkown named arguments are inputs with artefact lists.
        '''
        CLIActionBase.__init__(self, actionTag, alwaysDo, session, additionalActionProps,
                               actionID=actionID, actionConfig=actionConfig,
                               propInheritanceDict=propInheritanceDict)

        self._indicateCallable = indicateCallable
        self._outputextension = defaultoutputextension

        self._inputs = dict()
        self._args = dict()
        self._resultArtefacts = None

        self._argPositions = argPositions
        if argPositions is None:
            self._argPositions = list()

        if illegalArgs is None:
            illegalArgs = list()

        for name in inputArgs:
            if name in illegalArgs:
                raise RuntimeError('Action is initalized with illegal argument "{}". The argument is explicitly defined'
                                   ' as illegal argument.'.format(name))
            input = self._ensureArtefacts(inputArgs[name], name=name)
            if input is None:
                raise ValueError(
                    'Input argument is invalid as it does not contain artefact instances or is None/empty. Input name: {}'.format(name))
            self._inputs[name] = input
        self._addInputArtefacts(**self._inputs)

        if len(self._inputs)==0:
            raise RuntimeError('Action is not initialized with any artefact inputs')

        self._outputFlags = outputFlags
        if self._outputFlags is None:
            self._outputFlags = list()

        for flag in self._outputFlags:
            if flag in illegalArgs:
                raise RuntimeError('Action is initalized with illegal output flag "{}". The argument is explicitly defined'
                                   ' as illegal argument.'.format(flag))
            if flag in self._inputs:
                raise RuntimeError('Action is initalized with violating output flag "{}". The is already reserved/used'
                                   ' for an input.'.format(flag))


        self._cliArgs = dict()
        if cliArgs is not None:
            allIllegalArgs = list(self._inputs.keys())+illegalArgs
            if self._outputFlags is not None:
                allIllegalArgs = allIllegalArgs+self._outputFlags

            for argName in cliArgs:
                if argName not in allIllegalArgs:
                    self._cliArgs[argName] = cliArgs[argName]
                else:
                    raise RuntimeError('Action is initalized with illegal argument "{}". The argument will be set by'
                                       'the action (either as input and output or is explicitly defined illegal argument.'.format(argName))

    def _generateName(self):
        name = '{}'.format(self._actionID)
        for inputKey in self._inputs:
            name += '_{}'.format(artefactHelper.getArtefactShortName(self._inputs[inputKey][0]))
        return name

    def _indicateOutputs(self):
        allargs = self._inputs.copy()
        allargs.update(self._cliArgs)
        if self._indicateCallable is not None:
            self._resultArtefacts = self._indicateCallable(actionInstance=self, **allargs)
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
            self._resultArtefacts = [
                self.generateArtefact(self._inputs[sorted(self._inputs.keys())[0]][0],
                                      userDefinedProps={artefactProps.TYPE: artefactProps.TYPE_VALUE_RESULT},
                                      urlHumanPrefix=self.instanceName,
                                      urlExtension=self._outputextension)]
        return self._resultArtefacts

    def _prepareCLIExecution(self):
        try:
            execURL = AVIDUrlLocater.getExecutableURL(self._session, self._actionID, self._actionConfig)

            artefactArgs = self._inputs.copy()
            argPositions = self._argPositions.copy()

            for pos, resultArtefact in enumerate(self._resultArtefacts):
                resultPath = artefactHelper.getArtefactProperty(resultArtefact, artefactProps.URL)
                osChecker.checkAndCreateDir(os.path.split(resultPath)[0])

                key = "output_{}".format(pos)
                try:
                    key = self._outputFlags[pos]
                except:
                    argPositions.append(key)
                artefactArgs[key] = [resultArtefact]

            content = generate_cli_call(exec_url=execURL, artefact_args=artefactArgs, cli_args=self._cliArgs,
                                        arg_positions=argPositions)

        except:
            logger.error("Error for getExecutable.")
            raise

        return content
