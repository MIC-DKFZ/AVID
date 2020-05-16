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
from builtins import object
import argparse
import os

from avid.common.artefact import artefactExists
from avid.common.artefact.fileHelper import saveArtefactList_xml as saveArtefactList

def splitall(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts

class DirectoryCrawler(object):
  '''Helper class that crawls to directory tree starting from the given rootPath.
  The crawler assumes that every file, that he founds is an potential artefact.
  The crawler will call the file functor to interpret the file. If the file
  functor returns the artefact the crawler enlists it to the result in the
  artefact list.
  @param ignoreExistingArtefacts If set to true artefacts returned by fileFunctor
  will only be added if they do not already exist in the artefact list.'''
  def __init__(self, rootPath, fileFunctor, ignoreExistingArtefacts = False):
    self._rootPath = rootPath
    self._fileFunctor = fileFunctor
    self._ignoreExistingArtefacts = ignoreExistingArtefacts
    
  def getArtefacts(self):
    artefacts = list()
    
    for root, dirs, files in os.walk(self._rootPath):
      
      relativePath = os.path.relpath(root, self._rootPath)
      pathParts = splitall(relativePath)
      
      for aFile in files:
        
        artefact = self._fileFunctor(pathParts,aFile, os.path.join(root, aFile))
        
        if artefact is not None and not (artefactExists(artefacts, artefact) and self._ignoreExistingArtefacts):
          artefacts.append(artefact)

    return artefacts
      
  
def runSimpleCrawlerScriptMain(fileFunction):
    '''This is a helper function that can be used if you want to write a crawler script that crawles a root directory
     and stores the results as file. This function will parse for command line arguments "root" (the root directory)
     and "output" (file path where to store the artefact list) and use the DirectoryCrawler accordingly.'''
    parser = argparse.ArgumentParser(description='Simple AVID artefact crawler script that can be used to index'
                                                 ' artefacts.')
    parser.add_argument('root', help='Path to the root directory where the crawler should start to crawl.')
    parser.add_argument('output', help='File path where the results of the crawl should be stored'
                                       ' (the found/indexed artefacts). If output already exists it will be'
                                       ' overwritten.')

    cliargs, unknown = parser.parse_known_args()

    crawler = DirectoryCrawler(cliargs.root, fileFunction, True)
    artefacts = crawler.getArtefacts()

    saveArtefactList(cliargs.output, artefacts)
