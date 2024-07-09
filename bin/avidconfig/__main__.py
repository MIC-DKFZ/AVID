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


from builtins import str
import argparse
from avid.common.AVIDUrlLocater import getToolsPath
from avid.common.AVIDUrlLocater import getAVIDConfigPath
from avid.common.AVIDUrlLocater import getToolConfigPath
from avid.common.AVIDUrlLocater import getDefaultToolsSourceConfigPath
from avid.common.AVIDUrlLocater import getToolConfigsPath
from avid.common.AVIDUrlLocater import getPackageSourcePath, getPackageToolsConfigPath

from avid.common.osChecker import checkAndCreateDir

import os
import configparser
import zipfile
from urllib.request import urlretrieve
import shutil


def getAndUnpackMITK(mitkSourceConfigPath, packagesPath, update=False):
  mitkSourceConfig = configparser.ConfigParser()
  mitkSourceConfig.read(mitkSourceConfigPath)

  # FOR NOW: ONLY WINDOWS
  url = mitkSourceConfig.get("windows", "url")
  filename = url.split("/")[-1]
  filepath = os.path.join(packagesPath, filename)
  print("Downloading MITK installer.")
  urlretrieve(url, filepath)

  with zipfile.ZipFile(filepath, "r") as zip_f:
    zip_f.extractall(packagesPath)

  mitkDir = os.path.join(packagesPath, "MITK")
  if os.path.isdir(mitkDir):
    if update:
      shutil.rmtree(mitkDir)
    else:
      raise Exception("Error. MITK-CmdApps already present in tools directory. If you want to replace the existing "
                      "CmdApps, use 'avidconfig tools update' instead.")

  os.rename(filepath[:-4], mitkDir)
  os.remove(filepath)   # delete .zip file
  return mitkDir


def getAllKnownPackages():
  return ["MITK"]


def getAllKnownTools(sourceConfigPath):
  '''
  returns a list of all tools mentioned in the source config
  ''' 
  sourceConfig = configparser.ConfigParser()
  sourceConfig.read(sourceConfigPath)
  
  return sourceConfig.sections()


def installPackage(packageName, toolsPath, localPackagePath):
    checkAndCreateDir(os.path.join(toolsPath, "packages"))
    packagesPath = os.path.join(toolsPath, "packages")

    packagePath = localPackagePath
    if packageName == "MITK":
      if packagePath is None:
        mitkSourceConfigPath = getPackageSourcePath("MITK")
        packagePath = getAndUnpackMITK(mitkSourceConfigPath, packagesPath, False)

    sourceConfig = configparser.ConfigParser()
    sourceConfig.read(getPackageToolsConfigPath(packageName))
    for toolName in sourceConfig.sections():
      installTool(toolName, toolsPath, packageName, packagePath)


def installTool(toolName, toolsPath, packageName, packagePath):
  """
  installs a tool in the given toolspath
  """
  sourceConfig = configparser.ConfigParser()
  sourceConfig.read(getPackageToolsConfigPath(packageName))
  print("Install tool {}. Package = {}".format(toolName, packageName))

  execPath = None

  if packageName == 'MITK':
    mitkCmdAppName = sourceConfig.get(toolName, 'executableName')
    execPath = os.path.join(packagePath, mitkCmdAppName + ".bat")

  if execPath is None:
    print(
      "Error. Executable for {} not provided. "
      "Make sure your tool is correctly set up in the tools-sources.config."
      .format(toolName)
    )
    return

  if not os.path.isfile(execPath):
    print(
      "Error. Executable {} not found. Please make sure you are using the correct path and a current version of "
      "the package.".format(execPath)
    )
    return

  toolConfigFilePath = getToolConfigPath(toolName, toolsPath=toolsPath, checkExistance=False)
  if os.path.isfile(toolConfigFilePath):
    print("Error. The config for this tool already exists. "
          "To update an existing tool, use 'avidconfig tools update instead")

  checkAndCreateDir(os.path.split(toolConfigFilePath)[0])
  with open(toolConfigFilePath, 'w') as configFile:
    config = configparser.ConfigParser()
    config.set('', 'exe', execPath)
    config.write(configFile)


def main():
  mainDesc = "A simple tool to configure the avid pipeline and it tool stack."
  parser = argparse.ArgumentParser(description = mainDesc)

  parser.add_argument('command', help = "Specifies the type of configuration that should be done. tools", choices = ['tools', 'settings', 'tool-settings'])
  parser.add_argument('subcommands', nargs= '*', help = "Optional sub commands.")
  parser.add_argument('--toolspath', help = 'Specifies the tools path root that should be used by avid. In mode "tools" this path will directly be used. In mode "settings" the file avid.config will be altered.')
  parser.add_argument('--force', action='store_true', help = 'Used in conjunction with the sub command "tool-settings". Forces the tools config file to be generated if it is not existing.')
  parser.add_argument ('--localPackagePath', help = 'Here you can provide a path to MITK in case you a already have a version installed locally.')

  args_dict = vars(parser.parse_args())

  #if 'command' in args_dict:
  if args_dict['command'] == "tools":
    if len(args_dict['subcommands']) == 0:
      print("Error. Command 'tools' has to specify a subcommand ('update', 'install', 'add').")
      return
    if args_dict['subcommands'][0] == "install":
      packages = args_dict['subcommands'][1:]
      toolsPath = getToolsPath(False)
      if args_dict['toolspath']:
        toolsPath = args_dict['toolspath']
      checkAndCreateDir(toolsPath)
      toolsSourceConfigPath = getDefaultToolsSourceConfigPath()
      localPackagePath = args_dict.get('localPackagePath')
      if len(packages) != 1 and localPackagePath:
        print("Error. For command argument '--localPackagePath', a single package name must be specified.")
        return
      if len(packages) == 0:
        packages = getAllKnownPackages()
        print("No tool package specified to be installed. Install all tool packages with defined sources: " + str(packages))
      for package in packages:
        installPackage(package, toolsPath, localPackagePath)
    elif args_dict['subcommands'][0] == "add":
      if len(args_dict['subcommands']) < 3:
        print(
        "Error. Command 'tools add' needs two aditional positional arguments (tool/action id, path to the executable).")
        return

      actionID = args_dict['subcommands'][1]
      execPath = args_dict['subcommands'][2]

      configFilePath = getToolConfigPath(actionID)



      if configFilePath is not None:
        print('Error. Cannot add a new tool "{}". Tool\'s config does already exist. Use command "tool-settings <action id> exe" to change existing configurations.'.format(actionID))
        return

      configFilePath = getToolConfigPath(actionID, checkExistance=False)
      checkAndCreateDir(os.path.split(configFilePath)[0])
      with open(configFilePath, 'w') as configFile:
        config = configparser.ConfigParser()
        config.set('', 'exe', execPath)
        config.write(configFile)

        print("Added tool {} with executable {}.".format(actionID, execPath))

    else:
      print("Error. Subcommand '%s' is not supported for command avidconfig tools." % args_dict['subcommands'][0])

  elif args_dict['command'] == "tool-settings":
    if len(args_dict['subcommands']) < 3:
      print("Error. Command 'settings' needs three additional positional arguments (tool id, settings name and value).")
      return
    else:
      actionID = args_dict['subcommands'][0]
      name = args_dict['subcommands'][1]
      value = args_dict['subcommands'][2]

      try:
        section, name = name.split('.',1)
      except:
        section = ''

      if section.lower() == 'default':
        section = ''

      if section is None or name is None or value is None:
        print("Error. Cannot save settings for tool %s. Specified setting name or value is invalid. (section: %s; name: %s; value: %s" % (actionID, section, name, value))
        return
        
      configFilePath = getToolConfigPath(actionID)

      if configFilePath is None:
        if not args_dict['force']:
          print('Error. Cannot save settings for tool %s. Config file of tool cannot be found. If you want to generate/enforce a config file, use the flag "--force".' % (actionID))
          return
        else:
          configFilePath = getToolConfigPath(actionID, checkExistance=False)
          checkAndCreateDir(os.path.split(configFilePath)[0])
          with open(configFilePath, 'w') as configFile:
            pass
      
      config = configparser.ConfigParser()
      config.read(configFilePath)
      if not section in config.sections() and not section == '':
        config.add_section(section)
      config.set(section, name, value)
      with open(configFilePath, 'w') as configFile:
        config.write(configFile)

      print("Set config of tool %s. [%s] %s = %s" % (actionID, section, name, value))

  elif args_dict['command'] == "settings":
    if len(args_dict['subcommands'])<2:
      print("Error. Command 'settings' needs two additional positional arguments (settings name and value).")
      return
    else:
      name = args_dict['subcommands'][0]
      value = args_dict['subcommands'][1]
      section, name = name.split('.',1)
      
      if section is None or name is None or value is None:
        print("Error. Cannot save settings. Specified setting name or value is invalid. (section: %s; name: %s; value: %s)" % (section, name, value))
        return
        
      configFilePath = getAVIDConfigPath()
      config = configparser.ConfigParser()
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
