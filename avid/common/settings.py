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

'''
Allows access to the general settings of avid
'''
import os
from avid.common.AVIDUrlLocater import getAVIDConfigPath
from configparser import ConfigParser

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
    config = configparser.ConfigParser()
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



