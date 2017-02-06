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
import sys
import shutil
import argparse
import threading
import avid.common.patientNumber as patientNumber
import avid.common.artefact.fileHelper as fileHelper
from avid.common.artefact import ensureValidPath
from avid.common.workflow.structure_definitions import loadStructurDefinition_xml
from avid.common import artefact

'''set when at least one session was initialized to ensure this stream is only
 generated once, even if multiple sessions are generated in one run (e.g. in tests)'''
stdoutlogstream = None

def initSession( sessionPath, name = None, expandPaths = False, bootstrapArtefacts = None, autoSave = False, debug = False, structDefinition = None, overwriteExistingSession = False):
  ''' Convenience method to init a session and load the artefact list of the
   if it is already present.
   @param sessionPath Path of the stored artefact list the session should use
   and the rootpath for the new session. If no artefact list is present it will
   just be the rootpath of the new session.
   @param name of the session.
   @param structDefinition Path to the structure definition file.
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
  
  session = Session(name, rootPath, autoSave = autoSave, debug = debug)
      
  #logging setup
  logginglevel = logging.INFO
  if debug:
    logginglevel = logging.DEBUG
  
  filemode = 'a'
  if overwriteExistingSession:
    filemode = 'w'
    
  logging.basicConfig(filename=sessionPath+".log", filemode = filemode, level=logginglevel, format='%(levelname)-8s %(asctime)s [MODULE] %(module)-20s [Message] %(message)s [Location] %(funcName)s in %(pathname)s %(lineno)d' )
  rootlogger = logging.getLogger()
  
  global stdoutlogstream
  
  if stdoutlogstream is None:    
    stdoutlogstream = logging.StreamHandler(sys.stdout)
    stdoutlogstream.setLevel(logging.INFO)
    streamFormater = logging.Formatter('%(asctime)-8s [%(levelname)s] %(message)s')
    stdoutlogstream.setFormatter(streamFormater)
    rootlogger.addHandler(stdoutlogstream)
  
  #result path setup
  
  rootResultPath = os.path.join(rootPath, name)
  if overwriteExistingSession and os.path.exists(rootResultPath):
    try:
      shutil.rmtree(rootResultPath)
    except:
      rootlogger.warn("Overwrite existing session activated, but could not remove existing old result data directory.")
      
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
    
def initSession_byCLIargs( sessionPath = None, **args):
  ''' Convenience method to init a session and load the artefact list of the
   if it is already present. In contrast to initSession() it offers the possibility
   to parse the cmdline and uses the argument values. The command line arguments
   are only used if the respective parameter is not directly passed with the function call.
   The command line arguments have the following format "--<parameter name>" (e.g. --expandPaths)
   For more details see also initSession. 
   '''
  parser = argparse.ArgumentParser()
  parser.add_argument('--sessionPath', help = "Flag has to jobs. 1) PAth identifies location where the session xml should be stored. If the file exists, the content will be read in and reused. After the session is finished all artefacts (including newly generated once) are stored back. 2) It defines the root location where all the data is stored.")
  parser.add_argument('--name', help = 'Name of the session result folder in the rootpath defined by sessionPath. If not set it will be "<sessionFile name>_session".')
  parser.add_argument('--expandPaths', help = 'Indicates if relative artefact path should be expanded when loading the data.')
  parser.add_argument('--bootstrapArtefacts', help = 'File with additional artefacts that should be loaded when the session is initialized.')
  parser.add_argument('--debug', action='store_true', help = 'Indicates that the session should also log debug information (Therefore the log is more verbose).')
  parser.add_argument('--overwriteExistingSession', action='store_true', help = 'Indicates that a session, of it exists should be overwritten. Old artefacts are ignored and the old result folder will be deleted before the session starts.')
  parser.add_argument('--structDefinition', help = 'Path to the file that defines all structures/structure pattern, that should/might be evaluated in the session.')
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
  
  return initSession(sessionPath, **args)  

   
class Session(object):
  def __init__(self, name = None, rootPath = None, autoSave = False, debug = False):
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

    self.actions = dict()
    self.artefacts = list()
    
    self.numberOfPatients = self.getNumberOfPatientsDecorator(patientNumber.getNumberOfPatients)

    self.autoSave = autoSave

    #indicates that the session runs in debug mode
    self.debug = debug


  def __del__(self):
    if self.autoSave:
      fileHelper.saveArtefactList_xml(self._lastStoredLocation, self.artefacts, self.rootPath)
    
    global currentGeneratedSession
    currentGeneratedSession = None


  def __enter__(self):
    return self


  def __exit__(self, exc_type, exc_value, traceback):
    if self.autoSave:
      logging.debug("Auto saving artefact of current session. File path: %s.", self._lastStoredLocation)
      fileHelper.saveArtefactList_xml(self._lastStoredLocation, self.artefacts, self.rootPath)
     
    logging.info("Successful actions: %s.", len(self.getSuccessfulActions()))
    logging.info("Skipped actions: %s.", len(self.getSkippedActions()))
    if len(self.getFailedActions()) is 0:
      logging.info("Failed actions: 0.")
    else:
      logging.error("FAILED ACTIONS: %s.", len(self.getFailedActions()))
    logging.info("Session finished. Feed me more...")

      
  @property
  def definedStructures(self):
    return self.structureDefinitions.keys()
  
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
          
          
  def addActionToken(self, actionToken):
      """Adds a action token to a workflow (with the session info)"""
      with self.lock:
        self.actions[actionToken.getActionTag()] = actionToken
        logging.debug("stored action token: %s",actionToken)
        
        return actionToken
    
  def addArtefact(self, artefactEntry, removeSimelar = False):
    ''' 
        This method adds an arbitrary artefact entry to the artefact list.
        @param removeSimelar If True the method checks if the session data contains
        a simelar entry. If yes the simelar entry will be removed.      
    ''' 
    with self.lock:
      self.artefacts = artefact.addArtefactToWorkflowData(self.artefacts, artefactEntry, removeSimelar)
    
  def getFailedActions(self):
      """Returns all actions of the session that have failed."""
      failedActions = []
      
      for anActionID in self.actions.keys():
          #check each action
          actionToken = self.actions[anActionID]
          if actionToken.isFailure():
              failedActions.append(actionToken)
      
      return failedActions

  def getSkippedActions(self):
    """Returns all actions of the session that have been skipped."""
    skippedActions = []

    for anActionID in self.actions.keys():
      # check each action
      actionToken = self.actions[anActionID]
      if actionToken.isSkipped():
        skippedActions.append(actionToken)

    return skippedActions

  def getSuccessfulActions(self):
    """Returns all actions of the session that have been successful."""
    succActions = []

    for anActionID in self.actions.keys():
      # check each action
      actionToken = self.actions[anActionID]
      if actionToken.isSuccess():
        succActions.append(actionToken)

    return succActions

  def hasFailedActions(self):
      """An project is defined as failed, if at least on action the project depends on has failed. Retruns true if the project is assumed as failed. Returns true if all actions were successful or skipped"""
      failedActions = self.getFailedActions()
              
      return len(failedActions) != 0

currentGeneratedSession = None
