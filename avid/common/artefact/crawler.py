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
from builtins import object
import argparse
import os
import logging
import sys
import concurrent.futures

from avid.common.artefact.fileHelper import save_artefacts_to_xml as saveArtefactList
from avid.common.artefact import ArtefactCollection

log_stdout = logging.StreamHandler(sys.stdout)
crawl_logger = logging.getLogger(__name__)
log_stdout = logging.StreamHandler(sys.stdout)
#log_stdout.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
log_stdout.setLevel(logging.INFO)
crawl_logger.addHandler(log_stdout)
crawl_logger.setLevel(logging.INFO)

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
    artefacts = ArtefactCollection()
    
    for root, dirs, files in os.walk(self._rootPath):
      
      relativePath = os.path.relpath(root, self._rootPath)
      pathParts = splitall(relativePath)
      
      for aFile in files:

        fullpath = os.path.join(root, aFile)
        artefact = self._fileFunctor(pathParts,aFile, fullpath)

        if artefact is None:
            crawl_logger.debug(f'Check "{fullpath}": Skipped')
        elif artefact in artefacts and self._ignoreExistingArtefacts:
            crawl_logger.info(f'Check "{fullpath}": Skipped as duplicate artefact')
        else:
            artefacts.add_artefact(artefact)
            crawl_logger.info(f'Check "{fullpath}": Added')

    return artefacts


def getArtefactsFromFolder(folder, files, functor, rootPath):
    """
    Helper function that crawls all the given files, which lie within folder, by calling a functor on each one.
    The functor gets an additional argument 'known_ids', a set by which duplicates (e.g. DICOM files belonging to the
    same series) can be filtered out. This logic has to be done in the functor.
    """
    relativePath = os.path.relpath(folder, rootPath)
    pathParts = splitall(relativePath)
    artefacts = {}
    known_ids = set()
    for aFile in files:
        fullpath = os.path.join(folder, aFile)
        artefact = functor(pathParts, aFile, fullpath, known_ids)
        artefacts[fullpath] = artefact
    return artefacts


class ParallelDirectoryCrawler(object):
    """Helper class that crawls a directory tree starting from the given rootPath.
    The crawler assumes that every file that he founds is a potential artefact.
    The crawler will call the file functor to interpret the file. If the file
    functor returns the artefact the crawler enlists it to the result in the
    artefact list.
    Crawling is distributed to n_threads parallel processes, which each go through a folder.
    @param ignoreExistingArtefacts If set to true artefacts returned by fileFunctor
    will only be added if they do not already exist in the artefact list."""

    def __init__(self, rootPath, fileFunctor, ignoreExistingArtefacts=False, n_threads=10):
        self._rootPath = rootPath
        self._fileFunctor = fileFunctor
        self._ignoreExistingArtefacts = ignoreExistingArtefacts
        self._n_threads = n_threads

    def getArtefacts(self):
        artefacts = ArtefactCollection()
        with concurrent.futures.ProcessPoolExecutor(max_workers=self._n_threads) as executor:
            futures = []
            for root, dirs, files in os.walk(self._rootPath):
                futures.append(executor.submit(getArtefactsFromFolder, root, files, self._fileFunctor, self._rootPath))

            for future in concurrent.futures.as_completed(futures):
                folder_artefacts = future.result()
                for fullpath, artefact in folder_artefacts.items():
                    if artefact is None:
                        crawl_logger.debug(f'Check "{fullpath}": Skipped')
                    elif artefact in artefacts and self._ignoreExistingArtefacts:
                        crawl_logger.info(f'Check "{fullpath}": Skipped as duplicate artefact')
                    else:
                        artefacts.add_artefact(artefact)
                        crawl_logger.info(f'Check "{fullpath}": Added')

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

    crawl_logger.info(f'Finished crawling. Number of generated artefacts: {len(artefacts)}')
    saveArtefactList(cliargs.output, artefacts)


def runParallelCrawlerScriptMain(fileFunction, n_threads=10):
    """This is a helper function that can be used if you want to write a crawler script that crawles a root directory
     and stores the results as file. This function will parse for command line arguments "root" (the root directory)
     and "output" (file path where to store the artefact list) and use the DirectoryCrawler accordingly."""
    parser = argparse.ArgumentParser(description='Simple AVID artefact crawler script that can be used to index'
                                                 ' artefacts.')
    parser.add_argument('root', help='Path to the root directory where the crawler should start to crawl.')
    parser.add_argument('output', help='File path where the results of the crawl should be stored'
                                       ' (the found/indexed artefacts). If output already exists it will be'
                                       ' overwritten.')
    parser.add_argument('n_threads', help='Number of processes that will crawl folders in parallel', default=1)

    cliargs, unknown = parser.parse_known_args()

    crawler = ParallelDirectoryCrawler(cliargs.root, fileFunction, True, n_threads=n_threads)
    artefacts = crawler.getArtefacts()

    crawl_logger.info(f'Finished crawling. Number of generated artefacts: {len(artefacts)}')
    saveArtefactList(cliargs.output, artefacts)