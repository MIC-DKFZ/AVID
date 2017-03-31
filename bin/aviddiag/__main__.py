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


import argparse
from avid.common.AVIDUrlLocater import getUtilityPath
from avid.common.AVIDUrlLocater import getAVIDConfigPath
from avid.common.AVIDUrlLocater import getToolConfigPath
from avid.common.AVIDUrlLocater import getAVIDProjectRootPath
from avid.common.AVIDUrlLocater import getDefaultToolsSourceConfigPath

from avid.common.osChecker import checkAndCreateDir

import os
import ConfigParser
import subprocess

def main():
  mainDesc = "A simple diagnostics tool to analyse AVID artefact files."
  parser = argparse.ArgumentParser(description = mainDesc)

  parser.add_argument('artefactfile', help = "Specifies the path to the artefact file that should be analyzed")
  parser.add_argument('command', help = "Specifies the type of analysation that should be done. modes", choices = ['show'])
  parser.add_argument('--invalids', help = 'Will only analyze or select invalid artefacts.',action='store_true')
  parser.add_argument('--roots', help = 'Will only analyze or select artefacts that have no input artefacts/sources.',action='store_true')
  parser.add_argument('--prime-invalids', help = 'Will only analyze or select invalid artefacts, that have only valid input artefact (or None) and are inputs themself. Therefore artefacts that "started" a problem. This flag overwrites --invalids',action='store_true')
  parser.add_argument('--sources', help = 'Will only analyze or select artefacts that are inputs for other artefacts.',action='store_true')

  args_dict = vars(parser.parse_args())

  #if 'command' in args_dict:
  if args_dict['command'] == "tools":
    if len(args_dict['subcommands']) == 0:
      print("Error. Command 'tools' has to specify a subcommand ('update', 'install').")
      exit
    else:
      if args_dict['subcommands'][0] == "install" or args_dict['subcommands'][0] == "update":
        doInstall = args_dict['subcommands'][0] == "install"
        tools = args_dict['subcommands'][1:]
        toolsPath = getUtilityPath(False)
        if not args_dict['toolspath'] is None:
          toolsPath = args_dict['toolspath']

        sourceConfigPath = getDefaultToolsSourceConfigPath()

        if len(tools) == 0:
          tools = getAllKnownTools(sourceConfigPath)
          print("No tool specified to be installed. Install all tools with defined sources: "+ str(tools))
        for tool in tools:
          if doInstall:
            installTool(tool, toolsPath, sourceConfigPath)
          else:
            updateTool(tool, toolsPath, sourceConfigPath)
      else:
        print("Error. Subcommand '%s' is not supported for command avidconfig tools." % args_dict['subcommands'][0])


  elif args_dict['command'] == "tool-settings":
    if len(args_dict['subcommands'])<3:
      print("Error. Command 'settings' needs two additional positional arguments (tool id, settings name and value).")
      exit
    else:
      actionID = args_dict['subcommands'][0]
      name = args_dict['subcommands'][1]
      value = args_dict['subcommands'][2]
      section, name = name.split('.',1)

      if section is None or name is None or value is None:
        print("Error. Cannot save settings for tool %s. Specified setting name or value is invalid. (section: %s; name: %s; value: %s" % (actionID, section, name, value))
        exit
        
      configFilePath = getToolConfigPath(actionID)

      if configFilePath is None:
        print("Error. Cannot save settings for tool %s. Config file of tool cannot be found." % (actionID))
        exit
      
      config = ConfigParser.ConfigParser()
      config.read(configFilePath)
      if not section in config.sections() and not section == 'default':
        config.add_section(section)
      config.set(section, name, value)
      with open(configFilePath, 'w') as configFile:
        config.write(configFile)

      print("Set config of tool %s. [%s] %s = %s" % (actionID, section, name, value))

  elif args_dict['command'] == "settings":
    if len(args_dict['subcommands'])<2:
      print("Error. Command 'settings' needs two additional positional arguments (settings name and value).")
      exit
    else:
      name = args_dict['subcommands'][0]
      value = args_dict['subcommands'][1]
      section, name = name.split('.',1)
      
      if section is None or name is None or value is None:
        print("Error. Cannot save settings. Specified setting name or value is invalid. (section: %s; name: %s; value: %s)" % (section, name, value))
        exit
        
      configFilePath = getAVIDConfigPath()
      config = ConfigParser.ConfigParser()
      config.read(configFilePath)
      if not section in config.sections():
        config.add_section(section)
      config.set(section, name, value)
      with open(configFilePath, 'w') as configFile:
        config.write(configFile)
      
      print("Set [%s] %s = %s" % (section, name, value))
    
  print('Config command finished.')
 
   
    

if __name__ == "__main__":
  main()