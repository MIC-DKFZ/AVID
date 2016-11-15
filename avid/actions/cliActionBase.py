from . import SingleActionBase
import subprocess
import logging
import os
import time
import avid.common.settings as AVIDSettings

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

  def __init__(self, actionTag, alwaysDo = False, session = None, additionalActionProps = None, cwd = None, actionConfig = None, propInheritanceDict = dict()):
    '''@param cwd Specifies the current working directory that should be used for the cli call'''
    SingleActionBase.__init__(self, actionTag,alwaysDo, session, additionalActionProps, propInheritanceDict = propInheritanceDict)
    self._cwd = cwd
    self._actionConfig = actionConfig
    self._logFilePath = None
    self._logErrorFilePath = None
    
  def _prepareCLIExecution(self):
    ''' Internal function that should prepare/generate everything that is needed
    for the CLI call to run properly (e.g. the batch/bash file that should be
    executed. Then the call should be returned as result of the method. '''
    raise NotImplementedError("Reimplement in a derived class to function correctly.")
    #Implement: generation of all needed artefact and preperation of the cli call
    pass
  
  def _postProcessCLIExecution(self):
    ''' Internal function that should postprocess everything that is needed
    after the CLI call to leaf the action and its result in a proper state. '''
    #Implement: if something should be done after the execution, do it here
    pass  
    
  def _generateOutputs(self):
    clicall = self._prepareCLIExecution()
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
          max_pause_count = AVIDSettings.getSetting(AVIDSettings.ACTION_TIMEOUT) / pause_duration
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
      
        if self._cwd is None:
          subprocess.call(clicall, stdout = logfile, stderr = errlogfile)
        else:
          subprocess.call(clicall, cwd = self._cwd, stdout = logfile, stderr = errlogfile)


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