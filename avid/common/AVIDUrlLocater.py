'''
   used to identify the location of a action specific tool.
  
   every action has to use this action tool location routines!
'''

import os
import logging
import ConfigParser

logger = logging.getLogger(__name__)

def getAVIDPackagePath():
  '''
  identifies the root dir of the AVID package dir
  '''
  # get the location of this file (to be precisely it's the .pyc)
  path = os.path.dirname(__file__)

  # navigate to the root dir - to do so we navigate the directory tree upwards 
  return os.path.split(path)[0]

def getAVIDProjectRootPath():
  '''
  identifies the root dir of the AVID project source dir
  '''
  # get the location of this file (to be precisely it's the .pyc)
  path = os.path.dirname(__file__)

  # navigate to the root dir - to do so we navigate the directory tree upwards 
  return os.path.split(os.path.split(path)[0])[0]

def getAVIDConfigPath():
  '''
  Gets the path to the AVID config file.
  '''
  return os.path.join(getAVIDProjectRootPath(), "avid.config")
   
def getDefaultToolsSourceConfigPath():
  '''
  Gets the path to the AVID config file.
  '''
  return os.path.join(getAVIDProjectRootPath(), "tools-sources.config")
   
      
def getUtilityPath(checkExistance = True): 
  '''
     identify the Utility root dir (here are the specific action subdirs located)
  '''
  toolspath = None
  configPath = getAVIDConfigPath()
    
  if os.path.isfile(configPath):
    config = ConfigParser.ConfigParser()
    config.read(configPath)
    toolspath = config.get('avid','toolspath') 
          
  if toolspath is None:
    rootPath = getAVIDProjectRootPath()
    toolspath = os.path.join(rootPath,"Utilities")
  
  if os.path.isdir(toolspath) or not checkExistance:
    return toolspath
  else:
    return None
  
def getToolConfigPath(actionID, workflowRootPath = None):
  ''' Helper functions that gets the path to the config file for the passed actionID
      If workflowRootPath is set it will be also checked 
     @param actionID of the action that requests the URL
     @param workflowRootPath Path of the workflow. If none it will be ignored.
     The following rules will used to determine the tool config path.
     1. check the path:workflowRootPath/tools/<actionID>/avidtool.config. If it is valid, return it else 2.
     2. check the path:<AVID toolspath>/<actionID>/avidtool.config. If it is valid, return it else 2. 
     3. check path:avidRoot/Utilities/<actionID>/avidtool.config. If it is valid, return it else 4.
     4. return None      
  '''
  configPath = None

  if not workflowRootPath is None:
    testPath = os.path.join(workflowRootPath, "tools", actionID, "avidtool.config")
    if os.path.isfile(testPath):
      configPath = testPath

  if configPath is None:
    try:
      testPath = os.path.join(getUtilityPath(), actionID, "avidtool.config")
      if os.path.isfile(testPath):
        configPath = testPath
    except:
      pass
  
  return configPath       


def getExecutableURL(workflow, actionID, actionConfig = None):
  '''
     returns url+executable for a actionID request
     @param actionID of the action that requests the URL
     @param actionConfig specifies if a certian configuration of an action should be used.
     1. checks if there is a valid tool in workflow.actionTools[actionID]. If there is, return it else 2.
     2. check the path:workflowRootPath/tools/<actionID>/avidtool.config. If it is valid, return it else 3.
     3. check the path:<AVID toolspath>/<actionID>/avidtool.config. If it is valid, return it else 4. 
     4. check path:avidRoot/Utilities/<defaultRelativePath>. If it is valid, return it else 5.
     5. return None
  '''
  returnURL = None

  if actionID in workflow.actionTools:
    #option 1
    returnURL = workflow.actionTools[actionID]

  if returnURL is None:
    #option 2-4
    toolconfigPath = getToolConfigPath(actionID, workflow.rootPath)
    if os.path.isfile(str(toolconfigPath)):
      config = ConfigParser.ConfigParser()
      config.read(toolconfigPath)
    
      configSection = 'default'
      if not actionConfig is None:
        configSection = str(actionConfig)
        
      execURL = config.get(configSection,'exe')
      
      if not os.path.isabs(execURL):
        execURL = os.path.join(os.path.dirname(toolconfigPath),execURL)
                  
      if os.path.isfile(execURL):
        returnURL = execURL        
   
  if not os.path.exists(returnURL):
    logger.debug('Found executable URL for action "%s" seems to be invalid. Found URL: %s', actionID, returnURL)
  
  return returnURL     


def getDefaultPath():
  '''
     returns a default path for actions
     This method is called if the action executable can't be found elsewhere see getExecutablePath()
  '''
  return getUtilityPath()       

def removeFileEnding(exe):
  return exe[:exe.find(".")]
   
  