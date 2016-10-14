'''
Created on 26.01.2016

@author: floca
'''
import os


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
  artefact list 
  '''
  def __init__(self, rootPath, fileFunctor = None):
    self._rootPath = rootPath
    self._fileFunctor = fileFunctor
    
  def getArtefacts(self):
    artefacts = list()
    
    for root, dirs, files in os.walk(self._rootPath):
      
      relativePath = os.path.relpath(root, self._rootPath)
      pathParts = splitall(relativePath)
      
      for aFile in files:
        
        artefact = self._fileFunctor(pathParts,aFile, os.path.join(root, aFile))
        
        if artefact is not None:
          artefacts.append(artefact)

    return artefacts
      
  
    
  
    
  