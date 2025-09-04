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
from pathlib import Path

from avid.common.artefact.fileHelper import save_artefacts_to_xml as saveArtefactList
from avid.common.artefact import ArtefactCollection
from avid.common.workflow import Progress

log_stdout = logging.StreamHandler(sys.stdout)
crawl_logger = logging.getLogger(__name__)
log_stdout = logging.StreamHandler(sys.stdout)
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


def getArtefactsFromFolder(folder, functor, rootPath):
    """
    Helper function that crawls all the given files, which lie within folder, by calling a functor on each one.
    The functor gets an additional argument 'known_ids', a set by which duplicates (e.g. DICOM files belonging to the
    same series) can be filtered out. This logic has to be done in the functor.
    """
    files = [filepath.path for filepath in os.scandir(folder) if filepath.is_file()]
    relativePath = os.path.relpath(folder, rootPath)
    pathParts = splitall(relativePath)
    artefacts = {}
    known_ids = set()
    for aFile in files:
        fullpath = os.path.join(folder, aFile)
        artefact = functor(pathParts, Path(aFile).name, fullpath, known_ids)
        artefacts[fullpath] = artefact
    return artefacts


def scan_directories(dir_path):
    for sub_dir in os.scandir(dir_path):
        if sub_dir.is_file() and sub_dir.name.endswith('.dcm'):
            break
        if sub_dir.is_dir():
            yield sub_dir
            for sub_sub_dir in scan_directories(sub_dir):
                yield sub_sub_dir


class DirectoryCrawler(object):
    """
    Helper class that crawls a directory tree starting from the given rootPath.
    The crawler assumes that every file that he finds is a potential artefact.
    The crawler will call the file functor to interpret the file. If the file
    functor returns the artefact the crawler enlists it to the result in the
    artefact list.
    Crawling is distributed to n_threads parallel processes, which each go through a folder.
    :param rootPath: Path to the root directory. All subdirectories will recursively be crawled through.
    :param fileFunctor: A callable or factory for callables, which will get called for each subdirectory.
    If fileFunctor is a factory, a new callable will be generated and reused within each subdirectory.
    :param ignoreExistingArtefacts: If set to true artefacts returned by fileFunctor
    will only be added if they do not already exist in the artefact list.
    :param n_processes: The number of parallel processes to run. (default: 1)
    """

    def __init__(self, rootPath, fileFunctor, ignoreExistingArtefacts=False, n_processes=1):
        self._rootPath = rootPath
        self._fileFunctor = fileFunctor
        self._ignoreExistingArtefacts = ignoreExistingArtefacts
        self._n_processes = n_processes

        self._functor_is_factory = False
        try:
            functor_test = self._fileFunctor()
            self._functor_is_factory = callable(functor_test)
        except:
            pass

    def getArtefacts(self):
        artefacts = ArtefactCollection()
        with concurrent.futures.ProcessPoolExecutor(max_workers=self._n_processes) as executor, Progress(transient=True) as progress:
            directory_scanning = progress.add_task("Found folders to scan")
            futures = []
            for root in scan_directories(self._rootPath):
                if self._functor_is_factory:
                    functor = self._fileFunctor()
                else:
                    functor = self._fileFunctor
                futures.append(executor.submit(getArtefactsFromFolder, root.path, functor, self._rootPath))
                progress.update(directory_scanning, advance=1)
            progress.console.print(f"\nFound a total of {len(futures)} folders to scan. Starting to analyse folders ...")

            directory_analysis = progress.add_task("Finished folders", total=len(futures))
            # currently unused. Keeping these for https://git.dkfz.de/mic/internal/avid/-/issues/35
            skipped, duplicates, added = 0, 0, 0
            for future in concurrent.futures.as_completed(futures):
                folder_artefacts = future.result()
                for fullpath, artefact in folder_artefacts.items():
                    if artefact is None:
                        skipped += 1
                    elif artefact in artefacts and self._ignoreExistingArtefacts:
                        duplicates += 1
                    else:
                        artefacts.add_artefact(artefact)
                        added += 1
                progress.update(directory_analysis, advance=1)

        return artefacts


def runCrawlerScriptMain(fileFunction):
    """This is a helper function that can be used if you want to write a crawler script that crawles a root directory
     and stores the results as file. This function will parse for command line arguments "root" (the root directory)
     and "output" (file path where to store the artefact list) and use the DirectoryCrawler accordingly."""
    parser = argparse.ArgumentParser(description='Simple AVID artefact crawler script that can be used to index'
                                                 ' artefacts.')
    parser.add_argument('root', help='Path to the root directory where the crawler should start to crawl.')
    parser.add_argument('output', help='File path where the results of the crawl should be stored'
                                       ' (the found/indexed artefacts). If output already exists it will be'
                                       ' overwritten.')
    parser.add_argument('--n_processes', help='Number of processes that will crawl folders in parallel', default=1, type=int)

    cliargs, unknown = parser.parse_known_args()

    crawler = DirectoryCrawler(cliargs.root, fileFunction, True, n_processes=cliargs.n_processes)
    artefacts = crawler.getArtefacts()

    crawl_logger.info(f'Finished crawling. Number of generated artefacts: {len(artefacts)}')
    saveArtefactList(cliargs.output, artefacts)
