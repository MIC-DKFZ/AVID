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

from . import SingleActionBase
import subprocess
import logging
import os
import time
import stat
import math

import avid.common.settings as AVIDSettings
import avid.common.artefact.defaultProps as artefactProps
import avid.common.artefact as artefactHelper
from avid.common import osChecker, AVIDUrlLocater

logger = logging.getLogger(__name__)

class CLIActionBase(SingleActionBase):
  '''Base action for all actions that have the following pattern:
  They prepare the execution of an command line (e.g. by generating the needed
  batch file(s) or input data) and then the command line will be executed. This
  is standardized by this class. Derived classes just need to implement
  indicateOutputs() and prepareCLIExecution(). The rest is done by the base class.
  In _prepareCLIExecution() everything should be prepared/generated that is needed
  for the CLI call to run properly. Then the call should be returned as result of
  the method.'''

  def __init__(self, actionTag, alwaysDo = False, session = None, additionalActionProps = None, cwd = None, actionID = None, actionConfig = None, propInheritanceDict = None):
    '''@param cwd Specifies the current working directory that should be used for the cli call.
    if not set explicitly, it will be deduced automatically by the specified tool/action '''
    SingleActionBase.__init__(self, actionTag,alwaysDo, session, additionalActionProps, propInheritanceDict = propInheritanceDict)
    self._actionID = actionID
    self._actionConfig = actionConfig
    self._cwd = cwd
    if self._cwd is None and self._actionID is not None:
      self._cwd = os.path.dirname(AVIDUrlLocater.getExecutableURL(self._session, actionID, actionConfig))

    self._logFilePath = None
    self._logErrorFilePath = None

  @property
  def cwd(self):
    '''returns the current working directory that is used by the action when executing the tool.'''
    return self._cwd

  @property
  def logFilePath(self):
    '''Returns the path of the log file that contains the std::out stream of the execution, the action instance
    is associated with. If it is None the action was not executed so far.'''
    return self._logFilePath

  @property
  def logErrorFilePath(self):
    '''Returns the path of the error log file that contains the std::error stream of the execution, the action
    instance is associated with. If it is None the action was not executed so far.'''
    return self._logErrorFilePath

  def _prepareCLIExecution(self):
    ''' Internal function that should prepare/generate everything that is needed
    for the CLI call to run properly (e.g. the batch/bash file that should be
    executed.
     @return The returnvalue is a string/stream containing all the instructions that
      should be executed in the command line. The CLIActionBase will store it into a shell script and
      execute it.'''
    raise NotImplementedError("Reimplement in a derived class to function correctly.")
    #Implement: generation of all needed artefact and preperation of the cli call
    pass
  
  def _postProcessCLIExecution(self):
    ''' Internal function that should postprocess everything that is needed
    after the CLI call to leaf the action and its result in a proper state. '''
    #Implement: if something should be done after the execution, do it here
    pass  

  def _generateCLIfile(self, content):
    '''helper function to generate the appropriated CLI file that should be executed.
       @return Returns the path to the file.'''

    #by policy the first artefact always determines the location and such.
    cliArtefact = self.generateArtefact(self.outputArtefacts[0], userDefinedProps={artefactProps.TYPE:artefactProps.TYPE_VALUE_MISC, artefactProps.FORMAT:artefactProps.FORMAT_VALUE_BAT})
    path = artefactHelper.generateArtefactPath(self._session, cliArtefact)
    cliName = os.path.join(path, os.path.split(artefactHelper.getArtefactProperty(self.outputArtefacts[0],artefactProps.URL))[1])

    if osChecker.isWindows():
      cliName = cliName + os.extsep + 'bat'
    else:
      cliName = cliName + os.extsep + 'sh'

    try:
      osChecker.checkAndCreateDir(path)
      with open(cliName, "w") as outputFile:
        outputFile.write(content)
        outputFile.close()

      if not osChecker.isWindows():
        st = os.stat(cliName)
        os.chmod(cliName,st.st_mode | stat.S_IXUSR )

    except:
      logger.error("Error when writing cli script. Location: %s.", cliName)
      raise

    return cliName

  def _generateOutputs(self):
    callcontent = self._prepareCLIExecution()
    clicall = self._generateCLIfile(callcontent)

    global logger
    
    try:
      filePath = clicall+os.extsep+"log"
      logfile = open(filePath, "w")
      self._logFilePath = filePath
    except:
      logfile = None
      logger.debug('Unable to generate log file for call: %s', clicall)
      
    try:
      filePath = clicall+os.extsep+"error.log"
      errlogfile = open(filePath, "w")
      self._logErrorFilePath = filePath
    except:
      errlogfile = None
      logger.debug('Unable to generate error log file for call: %s', clicall)
      
    try:
        returnValue = 0
        
        if os.path.isfile(clicall):
          #Fix for T20136. Unsatisfying solution, but found no better way on
          #windows. If you make the subprocess calls to batch files (thats the
          #reason for the isfile() check) directly you get random "Error 32"
          #file errors (File already opened by another process) caused
          #by opening the bat files, which are normally produced by the actions.
          #"os.rename" approach was the simpliest way to check os independent
          #if the process can access the bat file or if there is still a racing
          #condition.
          pause_duration = AVIDSettings.getSetting(AVIDSettings.SUBPROCESS_PAUSE) 
          max_pause_count = math.ceil( AVIDSettings.getSetting(AVIDSettings.ACTION_TIMEOUT) / pause_duration)
          pause_count = 0
          time.sleep(0.1)
          while True :
            try:
              os.rename(clicall, clicall)
              break
            except OSError as e:
              if pause_count < max_pause_count:
                time.sleep(pause_duration)
                pause_count = pause_count + 1
                logger.debug('"%s" is not accessible. Wait and try again.', clicall)
              else:
                break

        useShell = not osChecker.isWindows()
        if self._cwd is None:
          subprocess.call(clicall, stdout = logfile, stderr = errlogfile, shell=useShell)
        else:
          subprocess.call(clicall, cwd = self._cwd, stdout = logfile, stderr = errlogfile, shell=useShell)


        if returnValue == 0:
          logger.debug('Call "%s" finished and returned %s', clicall, returnValue)
        else:
          logger.error('Call "%s" finished and returned %s', clicall, returnValue)
		  
    finally:
      if logfile is not None:
        logfile.close()
      if errlogfile is not None:
        errlogfile.close()

    self._postProcessCLIExecution()