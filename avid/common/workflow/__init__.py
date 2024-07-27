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

import argparse
import logging
import os
import shutil
import sys
import threading
from builtins import object
from builtins import str

import avid.common.artefact.fileHelper as fileHelper
import avid.common.patientNumber as patientNumber
from avid.common import artefact
from avid.common.workflow.structure_definitions import loadStructurDefinition_xml

from rich.traceback import Traceback as RichTraceback
from rich.progress import Progress
from rich.console import Console
from rich import inspect as rich_inspect
from rich.panel import  Panel as RichPanel
from rich.columns import Columns as RichColumns
from rich.padding import Padding as RichPadding

'''set when at least one session was initialized to ensure this stream is only
 generated once, even if multiple sessions are generated in one run (e.g. in tests)'''
stdoutlogstream = None

def initSession( sessionPath, name = None, expandPaths = False, bootstrapArtefacts = None, autoSave = False,
                 interimSessionSave = False, debug = False, structDefinition = None, overwriteExistingSession = False, initLogging = True):
  ''' Convenience method to init a session and load the artefact list of the
   if it is already present.
   @param sessionPath Path of the stored artefact list the session should use
   and the rootpath for the new session. If no artefact list is present it will
   just be the rootpath of the new session.
   @param name of the session.
   @param structDefinition Path to the structure definition file.
   @param autoSave
   '''
  sessionExists = False
   
  if sessionPath is None:
    raise ValueError("Cannot initialize session. SessionPath is None")

  rootPath = os.path.split(sessionPath)[0]     
  
  if os.path.isfile(sessionPath):  
    sessionExists = True
  else:
    if not os.path.isdir(rootPath):
      os.makedirs(rootPath)
  
  if name is None:
    name = os.path.split(sessionPath)[1]+"_session"
  
  session = Session(name, rootPath, autoSave = autoSave or interimSessionSave,
                    interimSessionSave = interimSessionSave, debug = debug)
      
  #logging setup
  logginglevel = logging.INFO
  if debug:
    logginglevel = logging.DEBUG
  
  filemode = 'a'
  if overwriteExistingSession:
    filemode = 'w'
    
  if initLogging:
    logging.basicConfig(filename=sessionPath+".log", filemode = filemode, level=logginglevel, format='%(levelname)-8s %(asctime)s [Location] %(funcName)s in %(pathname)s %(lineno)d [Message] %(message)s' )

  rootlogger = logging.getLogger()

  if initLogging:
    global stdoutlogstream

    if stdoutlogstream is None:
      from rich.logging import RichHandler
      #stdoutlogstream = RichHandler()
      stdoutlogstream = logging.StreamHandler(sys.stdout)
      stdoutlogstream.setLevel(logging.ERROR)
      streamFormater = logging.Formatter('%(asctime)-8s [%(levelname)s] %(message)s')
      stdoutlogstream.setFormatter(streamFormater)
      rootlogger.addHandler(stdoutlogstream)
  
  #result path setup
  
  rootResultPath = os.path.join(rootPath, name)
  if overwriteExistingSession and os.path.exists(rootResultPath):
    try:
      shutil.rmtree(rootResultPath)
    except:
      rootlogger.warning("Overwrite existing session activated, but could not remove existing old result data directory.")
      
  #artefact setup
  artefacts = list()
  
  if sessionExists:
    if not overwriteExistingSession:
      artefacts = fileHelper.loadArtefactList_xml(sessionPath, expandPaths)
      rootlogger.debug("Number of artefacts loaded from session: %s. Session path: %s", len(artefacts), sessionPath)
    else:
      rootlogger.info("Old session was overwritten. Session path: %s", sessionPath)
         
  if bootstrapArtefacts is not None and len(artefacts) == 0:
    rootlogger.debug("Load artefacts from bootstrap file: %s", bootstrapArtefacts)
    artefacts = fileHelper.loadArtefactList_xml(bootstrapArtefacts, expandPaths)
    rootlogger.debug("Number of artefacts loaded from bootstrap file: %s.", len(artefacts))

    
  session.artefacts.extend(artefacts)
  
  #other setup stuff
  
  session._lastStoredLocation = sessionPath
         
  if structDefinition is not None:
    if not os.path.isfile(structDefinition):
      raise ValueError("Cannot initialize session. Structure definition file does not exist. File: "+str(structDefinition))
    else:
      session.structureDefinitions = loadStructurDefinition_xml(structDefinition)

 
  global currentGeneratedSession
  currentGeneratedSession = session
  
  return session

def getSessionParser(sessionPath = None):
    parser = argparse.ArgumentParser(add_help=False)

    if sessionPath is None:
        parser.add_argument('sessionPath', help="Flag has two jobs. 1) Path identifies location where the session xml"
                                                " should be stored. If the file exists, the content will be read in"
                                                " and reused. After the session is finished all artefacts (including"
                                                " newly generated once) are stored back. 2) It defines the root"
                                                " location where all the data is stored.")
    else:
        parser.add_argument('sessionPath', '-s', help="Flag has two jobs. 1) Path identifies location where the session"
                                                      " xml should be stored. If the file exists, the content will be"
                                                      " read in and reused. After the session is finished all artefacts"
                                                      " (including newly generated once) are stored back. 2) It defines"
                                                      " the root location where all the data is stored.")

    parser.add_argument('--name', '-n', help = 'Name of the session result folder in the rootpath defined by sessionPath. If not set it will be "<sessionFile name>_session".')
    parser.add_argument('--expandPaths', '-e', help = 'Indicates if relative artefact path should be expanded when loading the data.')
    parser.add_argument('--bootstrapArtefacts', '-b', help = 'File with additional artefacts that should be loaded when the session is initialized.')
    parser.add_argument('--debug', action='store_true', help = 'Indicates that the session should also log debug information (Therefore the log is more verbose).')
    parser.add_argument('--overwriteExistingSession', '-o', action='store_true', help = 'Indicates that a session, of it exists should be overwritten. Old artefacts are ignored and the old result folder will be deleted before the session starts.')
    parser.add_argument('--structDefinition', help = 'Path to the file that defines all structures/structure pattern, that should/might be evaluated in the session.')
    parser.add_argument('--noInterimSave', action='store_true', help = 'Indicates that a session, should one store its new state after everything is processed. If not set, '
                                                                             'the session file will be actualized with every new artefact stored in the session.')
    return parser

def initSession_byCLIargs( sessionPath = None, **args):
  ''' Convenience method to init a session and load the artefact list of the
   if it is already present. In contrast to initSession() it offers the possibility
   to parse the cmdline and uses the argument values. The command line arguments
   are only used if the respective parameter is not directly passed with the function call.
   The command line arguments have the following format "--<parameter name>" (e.g. --expandPaths)
   For more details see also initSession. 
   '''
  parser = getSessionParser(sessionPath=sessionPath)
  cliargs, unkown = parser.parse_known_args()

  if sessionPath is None and cliargs.sessionPath is not None:
    sessionPath = cliargs.sessionPath
  
  if not "name" in args and cliargs.name is not None:
    args["name"] = cliargs.name
  if not "expandPaths" in args and cliargs.expandPaths is not None:
    args["expandPaths"] = cliargs.expandPaths
  if not "bootstrapArtefacts" in args and cliargs.bootstrapArtefacts is not None:
    args["bootstrapArtefacts"] = cliargs.bootstrapArtefacts
  if not "debug" in args and cliargs.debug is not None:
    args["debug"] = cliargs.debug
  if not "overwriteExistingSession" in args and cliargs.overwriteExistingSession is not None:
    args["overwriteExistingSession"] = cliargs.overwriteExistingSession    
  if not "structDefinition" in args and cliargs.structDefinition is not None:
    args["structDefinition"] = cliargs.structDefinition
  if not "noInterimSave" in args and cliargs.noInterimSave is not None:
    args["interimSessionSave"] = not cliargs.overwriteExistingSession

  return initSession(sessionPath, **args)  

   
class Session(object):
  def __init__(self, name = None, rootPath = None, autoSave = False, interimSessionSave = False, debug = False):
    if name is None or rootPath is None:
      raise TypeError()
    
    self.lock = threading.RLock()
    #Workflow Name/ID
    self.name = name
    #Path of the workflow session root
    self._rootPath = rootPath
    
    self._lastStoredLocation = str()
    
    #Path for all code templates used by the workflow
    self.templatePath = str()
    
    #Dictionary where specific locations for the ActionTools can be stored
    self.actionTools = dict()
    
    #Dictionary where relevant structure names or patterns can be stored.
    #Patterns are regular expressions that specify which kind of structure names
    #are associated with the same lable/objective. The pattern feature is used
    #by several actions when handling dicom or virtuos structure sets.
    #Some actions assume that all keys of the dictionary are relevant/ should
    #be processed by the action if nothing is explicitly defined by the user. 
    self.structureDefinitions = dict()

    #List of all executed (SingleActionBase based) actions that where executed for that session
    self.executed_actions = list()
    self.artefacts = list()

    #That is a list of all batch actions assigned to this session.
    self._batch_actions = list()
    
    self.numberOfPatients = self.getNumberOfPatientsDecorator(patientNumber.getNumberOfPatients)

    self.autoSave = autoSave
    self.interimSessionSave = interimSessionSave

    #indicates that the session runs in debug mode
    self.debug = debug

    #indicates if the session has a defined console where information should be printed to.
    #This variabel can be explitly set but is also said by some methods if needed.
    #Remark: Information will be always printed into the log (if said) indipendent from the console.
    self._console = None

    # indicates if the session has a progress indicator active that should be used (e.g. if processed actions are
    # reported).
    self._progress_indicator = None
    # Lookup that is used to map an action tag to a task id for the progress indicator.
    # This lookup is only valid and set if a progress indicator is defined.
    self.__progress_task_lookup = dict()

  def __del__(self):
    global currentGeneratedSession
    if currentGeneratedSession == self:
      currentGeneratedSession = None


  def __enter__(self):
    return self


  def __exit__(self, exc_type, exc_value, traceback):
    if self.autoSave:
      logging.debug("Auto saving artefact of current session. File path: %s.", self._lastStoredLocation)
      fileHelper.saveArtefactList_xml(self._lastStoredLocation, self.artefacts, self.rootPath)
     
    logging.info("Successful actions: %s.", len(self.getSuccessfulActions()))
    logging.info("Skipped actions: %s.", len(self.getSkippedActions()))
    if len(self.getFailedActions()) == 0:
      logging.info("Failed actions: 0.")
    else:
      logging.error("FAILED ACTIONS: %s.", len(self.getFailedActions()))
    logging.info("Session finished. Feed me more...")

      
  @property
  def definedStructures(self):
    return list(self.structureDefinitions.keys())
  
  def hasStructurePattern(self, name):
    result = False
    if name in self.structureDefinitions:
      if self.structureDefinitions[name] is not None:
        result = True
    
    return result
      
  
  @property
  def rootPath(self):
    return self._rootPath

  @rootPath.setter
  def rootPath(self, value):
    with self.lock:
      if os.path.isdir(value):
        self._rootPath = value
        self._lastStoredLocation = str()
      else:
        raise TypeError('invalid workflow root path specified')

  @property
  def contentPath(self):
    """Path that is the root for all content/artefacts generated by the session."""
    return os.path.join(self.rootPath, self.name)

  @property
  def lastStoredLocationPath(self):
    """Path where the session last was stored to."""
    return self._lastStoredLocation

  def getNumberOfPatientsDecorator(self, patNoFunc):
    def inner():
      return patNoFunc(self.artefacts)
    return inner
                         
                         
  def setWorkflowActionTool(self, actionID, entry):
    ''' 
     adds a action entry to a dictionary and returns it
     overrides existing entry!
    ''' 
    with self.lock:    
      self.actionTools[actionID] = entry

  def addProcessedActionInstance(self, action):
      """Adds a action token to a workflow (with the session info)"""
      with self.lock:
          self.executed_actions.append(action)
          logging.debug("stored action token: %s", action)
          if action.isSuccess:
              if action.has_warnings:
                  self.print('W', end='')
              else:
                self.print('.', end='')
          elif action.isSkipped:
              self.print('S', end='')
          else:
              self.print('E', end='')

          if not self._progress_indicator is None:
              self._progress_indicator.update(task_id=self.__progress_task_lookup[action.actionTag],
                                              advance=1)

  def addArtefact(self, artefactEntry, removeSimelar = False):
    ''' 
        This method adds an arbitrary artefact entry to the artefact list.
        @param removeSimelar If True the method checks if the session data contains
        a simelar entry. If yes the simelar entry will be removed.      
    ''' 
    with self.lock:
      self.artefacts = artefact.addArtefactToWorkflowData(self.artefacts, artefactEntry, removeSimelar)
      try:
        if self.interimSessionSave:
          logging.debug("Auto saving artefact of current session. File path: %s.", self._lastStoredLocation)
          fileHelper.saveArtefactList_xml(self._lastStoredLocation, self.artefacts, self.rootPath)
      except:
        pass

  def getFailedActions(self):
      """Returns all actions of the session that have failed."""
      failedActions = []
      
      with self.lock:
          for action in self.executed_actions:
              #check each action
              if action.isFailure:
                  failedActions.append(action)
      
      return failedActions

  def getSkippedActions(self):
    """Returns all actions of the session that have been skipped."""
    skippedActions = []

    with self.lock:
      for action in self.executed_actions:
        if action.isSkipped:
          skippedActions.append(action)

    return skippedActions

  def getSuccessfulActions(self):
    """Returns all actions of the session that have been successful."""
    succActions = []

    with self.lock:
      for action in self.executed_actions:
        if action.isSuccess:
          succActions.append(action)

    return succActions

  def getSuccessfulActionsWithWarnings(self):
    """Returns all actions of the session that have been successful but with warnings."""
    succActions = []

    with self.lock:
      for action in self.executed_actions:
        if action.isSuccess and len(action.last_warnings)>0:
          succActions.append(action)

    return succActions

  def hasFailedActions(self):
      """An project is defined as failed, if at least on action the project depends on has failed. Retruns true if the project is assumed as failed. Returns true if all actions were successful or skipped"""
      failedActions = self.getFailedActions()
              
      return len(failedActions) != 0

  def registerBatchAction(self, batch_action):
      self._batch_actions.append(batch_action)

  def run_batches(self):

    self.executed_actions = list()

    if self._console is None:
      self._console = Console()

    if self._progress_indicator is None:
      self._progress_indicator = Progress(console=self._console)

    self.__progress_task_lookup = dict()
    task_batches = self._progress_indicator.add_task('Batches', total=len(self._batch_actions))
    for batch_action in self._batch_actions:
      self.__progress_task_lookup[batch_action.actionTag] = self._progress_indicator.add_task(f'{batch_action.actionTag}', total=None)

    self.print('AVID Perform batch actions on session "{}"'.format(self.name))
    self._console.rule()
    self.print_session_info()

    with self._progress_indicator:
      for batch_pos, batch_action in enumerate(self._batch_actions):
        self._console.rule(title='Batch action "{}" (batch {}/{})'.format(batch_action.actionTag, batch_pos+1, len(self._batch_actions)) )
        self.print('Start batch action "{}" (batch {}/{})'.format(batch_action.actionTag, batch_pos+1, len(self._batch_actions)))
        self.print('Prepare actions ')
        batch_action.generateActions()
        self.print('Generated action instances: {}'.format(len(batch_action._actions)))
        self._progress_indicator.update(task_id=self.__progress_task_lookup[batch_action.actionTag], total=len(batch_action._actions))

        self.print('Process actions ', end='')
        batch_action.do()
        self.print('\n')

        if batch_action.isFailure:
          self._console.rule(title=f'[red]Batch action "{batch_action.actionTag}" failed action diagnostics[/red]')
          failed_actions = batch_action.getFailedActions()
          for failed_action in failed_actions:
            print_action_diagnostics(failed_action, self._console)
            self._console.print('\n')

        self._progress_indicator.update(task_batches, advance=1)


  def print(self, *args,**nargs):
    if not self._console is None:
      self._console.print(*args, **nargs)

  def print_session_info(self):
    self.print(f'Session name: {self.name}')
    self.print(f'Session path: {self.rootPath}')
    self.print(f'Debug mode: {self.debug}')


def print_action_diagnostics(action, console, debug=False):
  console.print(f'Action tag: {action.actionTag}')
  console.print(f'Action instance UID: {action.actionInstanceUID}')
  color_modifier = ''
  if action.isSuccess:
    if action.has_warnings:
      color_modifier = '[yellow]'
    else:
      color_modifier = '[green]'
  elif action.isFailure:
    color_modifier = '[red]'

  console.print(f'Status: {color_modifier}{action.last_exec_state}')

  if debug:
    console.print('Instance inspection:')
    rich_inspect(action, private=True, docs=False)

  if action.has_warnings:
    warning_panels = list()
    for (pos, warning) in enumerate(action.last_warnings):
      detail_panels = list()
      (warn_detail, exception) = warning
      detail_panels.append(f'[bold]Details:[/bold]\n{warn_detail}\n')
      if not exception is None:
        detail_panels.append('[bold]Exception:[/bold]')
        detail_panels.append(RichTraceback.from_exception(exception.__class__, exception, exception.__traceback__))

      panel_title = f'Warning #{pos}'
      if action.isFailure:
        panel_title = f'Error #{pos}'

      warning_panels.append(RichPanel(RichColumns(detail_panels), title=panel_title))

    console.print('Instance warnings/errors:')
    warn_panel = RichPadding(RichColumns(warning_panels),pad=(0,0,0,4))
    console.print(warn_panel)

currentGeneratedSession = None
