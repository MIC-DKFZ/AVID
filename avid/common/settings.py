'''
Allows access to the general settings of avid
'''
import os
from avid.common.AVIDUrlLocater import getAVIDConfigPath
from ConfigParser import ConfigParser

SUBPROCESS_PAUSE = 'subprocess_pause'
ACTION_TIMEOUT = 'action_timeout'
TOOLSPATH = 'toolspath'

defaults = {
            SUBPROCESS_PAUSE: 2, #in [s]
            ACTION_TIMEOUT: 60 # in [s]
           }

def _getSettingFromConfigFile(name):
  '''
  checks of the setting 'name' is set in the avid.config file. If this is not the
  it will look in the default value map
  '''
  configFilePath = getAVIDConfigPath()
  
  try:
    config = ConfigParser.ConfigParser()
    config.read(configFilePath)
    return config.get('avid',name)
    
  except:
    return None

def getSetting(name):
  '''
  checks of the setting 'name' is set in the avid.config file.
  If this is not the case it will look in the default value dictionary.
  If nothing can be found None will be returned.
  '''
  value = _getSettingFromConfigFile(name)
  
  if value is None:
    try:
      return defaults[name]
    except:
      return None
    
def getToolsPath():
  '''
  Convinience method to get the toolspath settings.
  '''
  return getSetting(TOOLSPATH)



