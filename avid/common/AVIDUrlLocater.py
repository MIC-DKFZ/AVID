'''
   used to identify the location of a action specific tool.
  
   every action has to use this action tool location routines!
  
   1. checks if there is a valid tool in workflow.actionTools[actionID] if there is return it else 2.
   2. check path:workflowRootPath/tools/<defaultName-dir>/defaultName if there is return it else 4.
   3. check path:avidRoot/Utilities/<defaultName-dir>/defaultName if there is return it else 4.
   4. return default value
'''

import os
import logging

logger = logging.getLogger(__name__)

def getAVIDRootPath():
  '''
  identifies the root dir of the AVID source dir
  '''
  # get the location of this file (to be precisely it's the .pyc)
  path = os.path.dirname(__file__)

  # navigate to the root dir - to do so we navigate the directory tree upwards 
  return os.path.split(os.path.split(os.path.split(path)[0])[0])[0]


def getUtilityPath(): 
  '''
     identify the Utility root dir (here are the specific action subdirs located)
  '''  
  rootPath = getAVIDRootPath()
  actionToolRootPath = os.path.join(rootPath,"Utilities")
  if os.path.isdir(actionToolRootPath):
    return actionToolRootPath
  else:
    return None
 
def getExecutableURL(workflow, actionID, defaultRelativePath):
  '''
     returns url+executable for a actionID request
     @param actionID of the action that requests the URL 
     @defaultRelativePath relative path to the action executable that should be used if no user definition
     exists.
     1. checks if there is a valid tool in workflow.actionTools[actionID] if there is return it else 2.
     2. check path:workflowRootPath/tools/<defaultRelativePath> if there is return it else 3.
     3. check path:avidRoot/Utilities/<defaultRelativePath> if there is return it else 4.
     4. return default value
  '''
  returnURL = None

  if actionID in workflow.actionTools:
    returnURL = workflow.actionTools[actionID]

  if returnURL is None:
    if not workflow.rootPath:
      print "Warning: no workflowRootPath set"
    actionPath = os.path.join(os.path.join(workflow.rootPath,"tools"),defaultRelativePath)
    if os.path.isfile(actionPath):
      returnURL = actionPath

  if returnURL is None:
    actionRootPath = getUtilityPath()
    if not actionRootPath is None:
      actionPath = os.path.join(actionRootPath,defaultRelativePath)
      if os.path.isfile(actionPath):
        returnURL = actionPath

  if returnURL is None:
    returnURL = defaultRelativePath
    
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
   
  