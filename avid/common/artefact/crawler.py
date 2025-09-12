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
import re
import concurrent.futures
from pathlib import Path
from typing import Callable, Optional, Pattern, Any
from functools import wraps

from avid.common.artefact.fileHelper import save_artefacts_to_xml as saveArtefactList
from avid.common.artefact import ArtefactCollection, Artefact
import avid.common.artefact.defaultProps as ArtefactProps
from avid.common.workflow import Progress

log_stdout = logging.StreamHandler(sys.stdout)
crawl_logger = logging.getLogger(__name__)
log_stdout = logging.StreamHandler(sys.stdout)
log_stdout.setLevel(logging.INFO)
crawl_logger.addHandler(log_stdout)
crawl_logger.setLevel(logging.INFO)


def crawl_filter_by_filename(filename_exclude : str | list[str] | None = None,
                 ext_include : Optional[tuple[str]] = None,
                 ext_exclude : Optional[tuple[str]] = None) -> Callable :

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(filename, *args, **kwargs):
            if filename_exclude:
                if isinstance(filename_exclude, str):
                    invalid_names = [filename_exclude]
                else:
                    invalid_names = list(filename_exclude)  # allows tuple, set, etc.

                for name in invalid_names:
                    if name == filename:
                        return None

            if ext_include:
                if not filename.endswith(ext_include):
                    return None

            if ext_exclude:
                if filename.endswith(ext_exclude):
                    return None

            #it is a potential artefact candidate, so call the function
            if not 'artefact_candidate' in kwargs:
                kwargs['artefact_candidate'] = Artefact()

            return func(filename=filename, *args, **kwargs)
        return wrapper
    return decorator

def crawl_property_by_path(property_map : dict[int, str], add_none:bool = False) -> Callable :
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(path_parts, *args, **kwargs):
            prop_values = dict()
            for pos, key in property_map.items():
                if -len(path_parts) <= pos < len(path_parts):
                    prop_values[key] = path_parts[pos]
                elif add_none:
                    prop_values[key] = None

            #now set all the found property mappings to the artefact candidate
            if not 'artefact_candidate' in kwargs:
                kwargs['artefact_candidate'] = Artefact()

            for property_name in prop_values:
                kwargs['artefact_candidate'][property_name] = prop_values[property_name]

            return func(path_parts=path_parts, *args, **kwargs)
        return wrapper
    return decorator

def crawl_property_by_filename(extraction_rules: dict[str, tuple[str, Any]], add_none: bool = False) -> Callable :
    """
    Decorator to extract property values from the filename of a potential artefact.
    :param extraction_rules: dictionary of extraction rules for certain properties. Key of the dictionary
        indicates the property key for which a value should be captured. The value of the dictionary is a
        (regex_pattern, default_value) tuple. regex_pattern: regex with one capture group that will be used
        to get the value. default: fallback value if no match is found.
    :param add_none: Indicates if a property should be extracted if no match was found and the default value is None.
        If True the property with value None will be added. Otherwise the property will be skipped.

    Example:
        @crawl_property_by_filename({
            "case":(r"Case_(\w+)", "unknown"),
            "timePoint":(r"TS(\d+)", 0)
        })
        def fileFunction(path_parts, filename, full_path, *args, **kwargs):
            #do stuff

        fileFunction(filename="Case_Pat1_TS3.txt")
        # -> {'case': 'Pat1', 'timePoint': '3'}
    """
    # Precompile regexes up-front for performance
    try:
        compiled_rules: dict[str, tuple[Pattern[str], Any]] = {
            key: (re.compile(regex), default)
            for key, (regex, default) in extraction_rules.items()
        }
    except re.error as err:
        crawl_logger.error(f"Error when precompiling the regex to capture property values from filename. Check regex"
                           f" patterns. Error details: {err}")
        raise

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(filename, *args, **kwargs):
            prop_values = dict()

            for key, (regex, default) in compiled_rules.items():
                match = regex.search(filename)
                if match:
                    value = match.group(1)
                    prop_values[key] = value
                else:
                    value = default
                    if value or add_none:
                        prop_values[key] = value

            #now set all the found property mappings to the artefact candidate
            if not 'artefact_candidate' in kwargs:
                kwargs['artefact_candidate'] = Artefact()

            for property_name in prop_values:
                kwargs['artefact_candidate'][property_name] = prop_values[property_name]

            return func(filename=filename, *args, **kwargs)
        return wrapper
    return decorator


def _split_all(path):
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


def _get_artefacts_from_folder(folder, functor, rootPath):
    """
    Helper function that crawls all the given files, which lie within folder, by calling a functor on each one.
    The functor gets an additional argument 'known_ids', a set by which duplicates (e.g. DICOM files belonging to the
    same series) can be filtered out. This logic has to be done in the functor.
    """
    folder = Path(folder)
    files = [Path(entry.path) for entry in os.scandir(folder) if entry.is_file()]
    relativePath = folder.relative_to(rootPath)
    pathParts = relativePath.parts
    artefacts = {}
    known_ids = set()
    for aFile in files:
        full_path = str(aFile.resolve())
        artefact = functor(path_parts=pathParts, filename=aFile.name, full_path=full_path, known_ids=known_ids)
        if artefact and not artefact[ArtefactProps.INVALID]:
            # if invalidity is not set already assume it is false in context of crawling,
            # therefore the file does exist otherwise the artefact wouldn't have been created
            artefact[ArtefactProps.INVALID] = False
        artefacts[full_path] = artefact
    return artefacts


def _scan_directories(dir_path: str | Path):
    dir_path = Path(dir_path)
    yield dir_path  # include top-level directory in the scanning

    for sub_entry in dir_path.iterdir():
        if sub_entry.is_file() and sub_entry.name.endswith('.dcm'):
            break
        if sub_entry.is_dir():
            yield from _scan_directories(sub_entry)

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
        self._last_irrelevant = 0
        self._last_skipped_duplicates = 0
        self._last_added = 0

        self._functor_is_factory = False
        try:
            functor_test = self._fileFunctor()
            self._functor_is_factory = callable(functor_test)
        except:
            pass

    @property
    def number_of_last_irrelevant(self):
        """ Returns the number of irrelevant file (not ended up in artefats) of the last crawl."""
        return self._last_irrelevant

    @property
    def number_of_last_skipped_duplicates(self):
        """ Returns the number of artefacts that where skipped due to being duplicates in the last crawl."""
        return self._last_skipped_duplicates

    @property
    def number_of_last_added(self):
        """ Returns the number of artefacts that where added in the last crawl."""
        return self._last_added

    def getArtefacts(self):
        artefacts = ArtefactCollection()
        with concurrent.futures.ProcessPoolExecutor(max_workers=self._n_processes) as executor, Progress(transient=True) as progress:
            directory_scanning = progress.add_task("Found folders to scan")
            futures = []
            for target_dir in _scan_directories(self._rootPath):
                if self._functor_is_factory:
                    functor = self._fileFunctor()
                else:
                    functor = self._fileFunctor
                progress.update(directory_scanning, advance=1)
                futures.append(executor.submit(_get_artefacts_from_folder, str(target_dir), functor, self._rootPath))
            progress.console.print(f"\nFound a total of {len(futures)} folders to scan. Starting to analyse folders ...")

            directory_analysis = progress.add_task("Finished folders", total=len(futures))
            self._last_irrelevant, self._last_skipped_duplicates, self._last_added = 0, 0, 0
            for future in concurrent.futures.as_completed(futures):
                folder_artefacts = future.result()
                for fullpath, artefact in folder_artefacts.items():
                    if artefact is None:
                        self._last_irrelevant += 1
                    elif artefact in artefacts and self._ignoreExistingArtefacts:
                        self._last_skipped_duplicates += 1
                    else:
                        artefacts.add_artefact(artefact)
                        self._last_added += 1
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
    parser.add_argument('--relative_paths', action='store_true', help = 'Indicates if the artefact url paths should be '
                                                                        'stored relative to the output path.')
    cliargs, unknown = parser.parse_known_args()

    crawler = DirectoryCrawler(cliargs.root, fileFunction, True, n_processes=cliargs.n_processes)
    artefacts = crawler.getArtefacts()

    crawl_logger.info(f'Finished crawling. Number of generated artefacts: {len(artefacts)}')
    saveArtefactList(filePath=cliargs.output, artefacts=artefacts, savePathsRelative=cliargs.relative_paths)
