# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from distutils.cmd import Command as SetupCommand
import os

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

TOOLS_SVN_URL = ''


class ToolsCommand(SetupCommand):
  description = 'Sets up the tools directory and its environment variable for AVID.'
  user_options = [
                  ('tool-path=', None, 'path where the tools are located or should be located afterwards'),
                  ('svn-url=', None, 'URL to SVN where the tools are located at will be fetched from, if no local tools can be found')
                  ]
  
  def initialize_options(self):
    """Set default values for options."""
    # Each user option must be listed here with their default value.
    self.tool_path = os.environ.get('AVID_TOOL_PATH')
      
    global TOOLS_SVN_URL
    svn_url = TOOLS_SVN_URL

  def finalize_options(self):
    """Post-process options."""

  def run(self):
    """Run command."""

    if self.tool_path is None:
      self.announce('ERROR. Neither a tool path is specified by user nor defined as variable for the system.',3)
      return
      
    if not os.path.exists(self.tool_path):
      #not on the local machine so get it
      self.announce('Download tools package: '+self.svn_url)
      os.mkdir(self.tool_path)
      p = subprocess.Popen('svn export "'+self.svn_url+'" "'+self.tool_path+'"', shell=True)
      
    if not os.environ.get('AVID_TOOL_PATH') is self.tool_path :
      #set or reset the environmental variable to the new path 
      os.environ['AVID_TOOL_PATH'] = self.tool_path
      self.announce('Set environment variable AVID_TOOL_PATH: '+self.tool_path)
      

setup(
    name='AVID',
    version='0.0.1',
    description='AVID project',
    long_description=readme,
    # if you want, put your own name here
    # (this would likely result in people sending you emails)
    author='SIDT@DKFZ',
    author_email='r.floca@dkfz.de',
    url='http://mitk.org',
    license=license,
    packages=find_packages(exclude=('tests', 'doc', 'tutorials', 'templates')),
    # the requirements to install this project.
    # Since this one is so simple this is empty.
    install_requires=[],
    # a more sophisticated project might have something like:
    #install_requires=['numpy>=1.11.0', 'scipy>=0.17', 'scikit-learn']

    # after running setup.py, you will be able to call samplepackage_exe
    # from the console as if it was a normal binary. It will call the function
    # main in bin/samplepackage_exe.py
    entry_points={
        'console_scripts': ['samplepackage_exe=bin.samplepackage_exe:main'],
    },
    cmdclass={'tools': ToolsCommand,}
)

