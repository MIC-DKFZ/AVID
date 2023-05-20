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

from avid.common import osChecker, AVIDUrlLocater, cliConnector

from .cliActionBase import CLIActionBase

logger = logging.getLogger(__name__)


def _generateFlag(flagName):
    if len(flagName) == 1:
        return '-{}'.format(flagName)
    else:
        return '--{}'.format(flagName)


def _generateAdditionalArgValueString(arg_value):
    result = ''
    if isinstance(arg_value, list):
        for value in arg_value:
            result += '"{}" '.format(value)
        result.strip()
    else:
        result = '"{}"'.format(arg_value)
    return result


def generate_cli_call(exec_url, artefact_args, additional_args=None, arg_positions=None,
                      artefact_url_extraction_delegate=None):
    """Helper that generates the the cli call string for a given set of artefact selection arguments and normal
    arguments.
    :param exec_url: The argument for the cli itself.
    :param artefact_args: Dictionary of artefact selections as values. The key is the flag (without "-" or "--"; they
    will be added automatically depending on the size of the key; one character keys will completed with "-", others
    with "--"). If the selection contains more then one artefact all artefact urls will be added as single arguments
    after the flag.
    :param additional_args: Dictionary with all additional arguments (except the artefact inputs and outputs) that
    should be passed to the cli. The key is the argument/flag name (without "-" or "--"; they will be added
    automatically depending on the size of the key; one character keys will completed with "-", others with "--"). If
    the value is not None it will be also added after the argument. If the value of an additional argument is an
    list each list element will be added as escaped value.
    :param arg_positions: list that contains the keys of all arguments (from artefact_args and additional_args) that are
    not flag based but positional arguments. Those arguments will be added in the order of the list before the
    positional arguments.
    :param artefact_url_extraction_delegate: Delegate that can be used to change the way how urls are extracted from
    artefacts that are provided for the argument or to over a way to manipulate them before generating the cli call
    string. The default implementation (extract_artefact_arg_urls_default) does just return the URL of the artefact.
    The signature of the delegate is delegate(arg_name, arg_value). Arg_value is expected to be a list of artefacts.
    The return is expected to be a list of URL strings (or None for artefacts that should not return a URL).
    """
    extract_delegat = artefact_url_extraction_delegate
    if extract_delegat is None:
        extract_delegat = cliConnector.default_artefact_url_extraction_delegate

    content = '"{}"'.format(exec_url)
    if arg_positions is None:
        arg_positions = list()

    for key in arg_positions:
        if key in artefact_args:
            urls = extract_delegat(arg_name=key, arg_value=artefact_args[key])
            for artefactPath in urls:
                if artefactPath is not None:
                    content += ' "{}"'.format(artefactPath)
        elif additional_args is not None and key in additional_args:
            content += ' {}'.format(_generateAdditionalArgValueString(additional_args[key]))

    for pos, artefactKey in enumerate(artefact_args):
        if artefactKey not in arg_positions and artefact_args[artefactKey] is not None:
            artefact_content = ''
            urls = extract_delegat(arg_name=artefactKey, arg_value=artefact_args[artefactKey])
            for artefactPath in urls:
                if artefactPath is not None:
                    artefact_content += ' "{}"'.format(artefactPath)

            if len(artefact_content) > 0:
                content += ' {}'.format(_generateFlag(artefactKey)) + artefact_content

    if additional_args is not None:
        for argKey in additional_args:
            if argKey not in arg_positions:
                content += ' {}'.format(_generateFlag(argKey))
                if additional_args[argKey] is not None:
                    content += ' {}'.format(_generateAdditionalArgValueString(additional_args[argKey]))

    return content


class GenericCLIAction(CLIActionBase):
    """Action that offers a generic wrapper around a cli execution of an action. The basic idea is to have a simple
     possibility to define an action that execute a CLI executable. All passed artefact selections are directly
     converted into cli arguments. The user can define additional cli arguments and if the arguments are flag based
     or positional arguments. If a user wants to use a tool not known to AVID, the users can specify own actionID and
     configure it with avidconig (system wide) or at runtime for a specific session (setWorkflowActionTool()) to point
     to a certain executable. For more details see the documentation of __init_."""

    def __init__(self, actionID, outputFlags=None, indicateCallable=None, additionalArgs=None, illegalArgs=None,
                 argPositions=None, noOutputArgs=False, outputReferenceArtefactName=None, defaultoutputextension='nrrd',
                 postProcessCLIExecutionCallable=None, collectOutputsCallable=None, additionalArgsAsURL=None,
                 inputArgsURLExtractionDelegate=None, actionTag="GenericCLI", alwaysDo=False, session=None,
                 additionalActionProps=None, actionConfig=None, propInheritanceDict=None, cli_connector=None,
                 **inputArgs):
        """
        :param actionID: actionID that will be used to deduce the tool/executable for this action instance.
        :param outputFlags: The argument/flag name (without "-" or "--"; the will be added automatically) of the output.
        If set to none, the action assumes that the output parameter are indexed by and directly added in the beginning
        as the last parameters without a flag. If you don't want to use a flag, but control the position of the output
        parameter. Define a output flag (or keep the default 'o') and use the argPositions to control the position
        of all arguments.
        :param argPositions: list that contains the keys of all arguments (from artefact_args and additional_args) that are
        not flag based but positional arguments. Those arguments will be added in the order of the list before the
        positional arguments.
        :param indicateCallable: A callable that, if defined, will be called to query the outputs. The action assumes
        that the callable returns a list of output artefacts or None (if no indication can be made; like
        self.indicateOutputs). If this callable is not set, the default is one output that will be defined by the action
        and uses the first input artefact as reference. The signature of indicateCallable is:
        indicateCallable(actionInstance = Instance of the calling action),
        **allArgs = all arguments passed to the action))
        :param postProcessCLIExecutionCallable: A callable that, if defined, will be called to execute post processing
        code after the CLI Execution. If this callable is not set, no post processing will be done. The signature of
        postProcessCLIExecutionCallable is:
        postProcessCLIExecutionCallable(actionInstance = Instance of the calling action, **allArgs = all arguments
        passed to the action)
        :param collectOutputsCallable: A callable that, if defined, will be called to collect/generate artefact
        instances for all generated outputs after the CLI execution is post processed. For more details, See the
        documentation of SingleActionBase._collectOutputs. If this callable is not set, nothing will be collected and
        the indicated outputs are assumed to be still correct. The signature of the callable is:
        collectOutputsCallable(actionInstance = instance of the calling action,
         indicatedOutputs = outputs indicated so far, **allArgs = all arguments passed to the action )
        :param noOutputArgs: If set to true the output artefacts of the action will not be added as output args. In this
        case outputFlags will be ignored.
        :param outputReferenceArtefactName: Name of the inputArgs that will be used as
        template when generating the output artefacts. If not set (None), the first input selection (in alphabetic
        order) will be used. If indicateCallable is set, this argument has only impact if the callable makes use of it.
        :param defaultoutputextension: Output extension that should be used if no indicateCallable is defined.
        :param additionalArgs: Dictionary with all additional arguments (except the artefact inputs and outputs) that
        should be passed to the cli. The key is the argument/flag name (without "-" or "--"; the will be added
        automatically). If the value is not None it will be also added after the argument.
        :param additionalArgsAsURL: List of names of additionalArgs whose values should be treated like
        URLs extracted from the input arguments. Depending on the OS or runtime environement that might lead to
        alterations of the values. E.g. due to mapping of the URLs. If a name in the list does not exist in
        additionalArgs, it is just ignored.
        :param illegalArgs: List that can be used to add additional forbidden argument names, that may not be contained
        in additionalArgs or inputArgs.
        :param inputArgsURLExtractionDelegate: Delegate that can be used to change the way how urls are extracted from
        artefacts that are provided for the argument or to offer a way to manipulate them before generating the cli
        call string. The default implementation (extract_artefact_arg_urls_default) does just return the URL of the
        artefact. The signature of the delegate is delegate(arg_name, arg_value). Arg_value is expected to be a list
        of artefacts. The return is expected to be a list of URL strings (or None for artefacts that should not
        return a URL).
        :param inputArgs: It is assumed that all unkown named arguments are inputs with artefact lists.
        """
        CLIActionBase.__init__(self, actionTag=actionTag, alwaysDo=alwaysDo, session=session,
                               additionalActionProps=additionalActionProps,
                               actionID=actionID, actionConfig=actionConfig,
                               propInheritanceDict=propInheritanceDict, cli_connector=cli_connector)

        self._indicateCallable = indicateCallable
        self._postProcessCLIExecutionCallable = postProcessCLIExecutionCallable
        self._inputArgsURLExtractionDelegate = inputArgsURLExtractionDelegate
        self._collectOutputsCallable = collectOutputsCallable
        self._outputextension = defaultoutputextension
        self._noOutputArgs = noOutputArgs

        self._inputs = dict()
        self._args = dict()

        self._argPositions = argPositions
        if argPositions is None:
            self._argPositions = list()

        self._illegalArgs = illegalArgs
        if illegalArgs is None:
            self._illegalArgs = list()

        self._additionalArgsAsURL = additionalArgsAsURL
        if additionalArgsAsURL is None:
            self._additionalArgsAsURL = list()

        for name in inputArgs:
            if name in self._illegalArgs:
                raise RuntimeError('Action is initalized with illegal argument "{}". The argument is explicitly defined'
                                   ' as illegal argument.'.format(name))
            try:
                inputArtefacts = self._ensureArtefacts(inputArgs[name], name=name)
            except Exception:
                raise RuntimeError('Action is initalized with invalid argument "{}". The unkown argument is not a list of'
                                   ' artefact and does not qualify as input. Value of invalid input argument: {}'.format(name, inputArgs[name]))

            if inputArtefacts is None:
                raise ValueError(
                    'Input argument is invalid as it does not contain artefact instances or is None/empty. Input name: {}'.format(
                        name))
            self._inputs[name] = inputArtefacts
        self._addInputArtefacts(**self._inputs)

        if len(self._inputs) == 0:
            raise RuntimeError('Action is not initialized with any artefact inputs')

        self._outputFlags = outputFlags
        if self._outputFlags is None:
            self._outputFlags = list()

        for flag in self._outputFlags:
            if flag in self._illegalArgs:
                raise RuntimeError(
                    'Action is initalized with illegal output flag "{}". The argument is explicitly defined'
                    ' as illegal argument.'.format(flag))
            if flag in self._inputs:
                raise RuntimeError('Action is initalized with violating output flag "{}". The is already reserved/used'
                                   ' for an input.'.format(flag))

        self._additionalArgs = dict()
        self.setAdditionalArguments(additionalArgs)

        self._outputReferenceArtefactName = outputReferenceArtefactName
        if self._outputReferenceArtefactName is not None:
            if self._outputReferenceArtefactName not in self._inputs:
                raise ValueError(
                    'Action cannot be initialized. Defined outputReferenceArtefactName ("{}") does not exist in the inputs dictionary: {}'.format(
                        self._outputReferenceArtefactName, self._inputs.keys()))

    def setAdditionalArguments(self, additionalArgs):
        """Method can be used to (re)set the additional arguments of the action instance.
        All passed arguments are assumed to be additional arguments with lists of argument values;
        like when you setting them directly in __init__(). If additional arguments where already set,
        the old ones will be overwritten."""
        self._additionalArgs = dict()
        if additionalArgs is not None:
            allIllegalArgs = list(self._inputs.keys()) + self._illegalArgs
            if self._outputFlags is not None:
                allIllegalArgs = allIllegalArgs + self._outputFlags

            for argName in additionalArgs:
                if argName not in allIllegalArgs:
                    self._additionalArgs[argName] = additionalArgs[argName]
                else:
                    raise RuntimeError('Action is initalized with illegal argument "{}". The argument will be set by'
                                       'the action (either as input and output or is explicitly defined illegal argument.'.format(
                        argName))

    def _generateName(self):
        name = '{}_{}'.format(self._actionID, self._actionTag)
        for inputKey in self._inputs:
            if self._inputs[inputKey] is not None and self._inputs[inputKey][0] is not None:
                name += '_{}_{}'.format(inputKey, artefactHelper.getArtefactShortName(self._inputs[inputKey][0]))
        return name

    def _indicateOutputs(self):
        resultArtefacts = None
        if self._indicateCallable is not None:
            allargs = self._inputs.copy()
            allargs.update(self._additionalArgs)
            resultArtefacts = self._indicateCallable(actionInstance=self, **allargs)
            if resultArtefacts is not None:
                # check if its really a list of artefacts
                try:
                    for artifact in resultArtefacts:
                        if not isinstance(artifact, artefactHelper.Artefact):
                            raise TypeError(
                                'Indicate callable does not return a list of artefacts. Please check callable. Erroneous return: {}'.format(
                                    artifact))
                except Exception:
                    raise TypeError(
                        'Indicate callable does not return a list of artefacts. Please check callable. Erroneous return: {}'.format(
                            resultArtefacts))

        else:
            # we generate the default as template the first artefact of the first input (sorted by input names) in the dictionary
            reference = self._inputs[sorted(self._inputs.keys())[0]][0]

            if self._outputReferenceArtefactName is not None:
                reference = self._inputs[self._outputReferenceArtefactName][0]

            resultArtefacts = [
                self.generateArtefact(reference=reference,
                                      userDefinedProps={artefactProps.TYPE: artefactProps.TYPE_VALUE_RESULT},
                                      urlHumanPrefix=self.instanceName,
                                      urlExtension=self._outputextension)]
        return resultArtefacts

    def _prepareCLIExecution(self):
        try:
            execURL = self._cli_connector.get_executable_url(self._session, self._actionID, self._actionConfig)

            artefactArgs = self._inputs.copy()
            argPositions = self._argPositions.copy()

            if not self._noOutputArgs:
                for pos, resultArtefact in enumerate(self.outputArtefacts):
                    resultPath = artefactHelper.getArtefactProperty(resultArtefact, artefactProps.URL)
                    osChecker.checkAndCreateDir(os.path.split(resultPath)[0])

                    key = "output_{}".format(pos)
                    try:
                        key = self._outputFlags[pos]
                    except Exception:
                        argPositions.append(key)
                    artefactArgs[key] = [resultArtefact]

            content = generate_cli_call(exec_url=execURL, artefact_args=artefactArgs,
                                        additional_args=self._additionalArgs,
                                        arg_positions=argPositions,
                                        artefact_url_extraction_delegate=self._cli_connector.get_artefact_url_extraction_delegate(self._inputArgsURLExtractionDelegate))

        except Exception:
            logger.error("Error for getExecutable.")
            raise

        return content

    def _postProcessCLIExecution(self):
        try:
            allargs = self._inputs.copy()
            allargs.update(self._additionalArgs)
            if self._postProcessCLIExecutionCallable is not None:
                self._postProcessCLIExecutionCallable(actionInstance=self, **allargs)
        except Exception:
            logger.error("Error while post processing in generic CLI action: {}.".format(self))
            raise

    def _collectOutputs(self, indicatedOutputs):
        collectedArtefacts = None
        if self._collectOutputsCallable is not None:
            allargs = self._inputs.copy()
            allargs.update(self._additionalArgs)

            collectedArtefacts = self._collectOutputsCallable(actionInstance=self, indicatedOutputs=indicatedOutputs,
                                                              **allargs)
            # check if its really a list of artefacts
            try:
                for artifact in collectedArtefacts:
                    if not isinstance(artifact, artefactHelper.Artefact):
                        raise TypeError(
                            'Indicate callable does not return a list of artefacts. Please check callable. Erroneous return: {}'.format(
                                artifact))
            except Exception:
                raise TypeError(
                    'Indicate callable does not return a list of artefacts. Please check callable. Erroneous return: {}'.format(
                        collectedArtefacts))

        else:
            collectedArtefacts = super()._collectOutputs(indicatedOutputs=indicatedOutputs)
        return collectedArtefacts
