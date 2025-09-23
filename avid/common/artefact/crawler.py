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

import argparse
import concurrent.futures
import logging
import os
import re
import sys
from builtins import object
from functools import wraps
from typing import Any, Callable, Dict, Generator, List, Optional, Pattern, Tuple, Union

import avid.common.artefact.defaultProps as ArtefactProps
from avid.common.artefact import Artefact, ArtefactCollection
from avid.common.artefact.fileHelper import save_artefacts_to_xml as saveArtefactList
from avid.common.workflow import Console, Progress

log_stdout = logging.StreamHandler(sys.stdout)
crawl_logger = logging.getLogger(__name__)
log_stdout = logging.StreamHandler(sys.stdout)
log_stdout.setLevel(logging.INFO)
crawl_logger.addHandler(log_stdout)
crawl_logger.setLevel(logging.INFO)


def crawl_filter_by_filename(
    filename_exclude: Optional[Union[str, List[str]]] = None,
    ext_include: Optional[Tuple[str, ...]] = None,
    ext_exclude: Optional[Tuple[str, ...]] = None,
) -> Callable:
    """Decorator to filter files based on filename patterns and extensions.

    :param filename_exclude: Single filename or list of filenames to exclude
    :param ext_include: Tuple of extensions to include (files must end with one of these)
    :param ext_exclude: Tuple of extensions to exclude
    :return: Decorated function that applies the filtering logic
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Optional[Artefact]:
            filename = kwargs["filename"]

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

            # It is a potential artefact candidate, so call the function
            if "artefact_candidate" not in kwargs:
                kwargs["artefact_candidate"] = Artefact()

            return func(*args, **kwargs)

        return wrapper

    return decorator


def crawl_property_by_path(
    property_map: Dict[int, str], add_none: bool = False
) -> Callable:
    """Decorator to extract properties from path parts.

    :param property_map: Dictionary mapping path position (int) to property key (str)
    :param add_none: Whether to add properties with None values when path position doesn't exist
    :return: Decorated function that applies path-part-based property extraction
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Optional[Artefact]:
            path_parts = kwargs["path_parts"]
            if "artefact_candidate" not in kwargs:
                kwargs["artefact_candidate"] = Artefact()

            for pos, key in property_map.items():
                if -len(path_parts) <= pos < len(path_parts):
                    kwargs["artefact_candidate"][key] = path_parts[pos]
                elif add_none:
                    kwargs["artefact_candidate"][key] = None

            return func(*args, **kwargs)

        return wrapper

    return decorator


def crawl_property_by_filename(
    extraction_rules: Dict[str, Tuple[str, Any]], add_none: bool = False
) -> Callable:
    """Decorator to extract property values from the filename of a potential artefact.

    :param extraction_rules: Dictionary of extraction rules for certain properties. Key indicates
        the property key for which a value should be captured. Value is a
        (regex_pattern, default_value) tuple. regex_pattern: regex with one capture group
        that will be used to get the value. default: fallback value if no match is found.
    :param add_none: Whether to add a property with None value if no match found and default is None.
    :return: Decorated function that applies filename-based property extraction

    Example::

        @crawl_property_by_filename({
            "case":(r"Case_(\w+)", "unknown"),
            "timePoint":(r"TS(\d+)", 0)
        })
        def file_function(path_parts, filename, full_path, *args, **kwargs):
            # do stuff

        file_function(filename="Case_Pat1_TS3.txt")
        # -> {'case': 'Pat1', 'timePoint': '3'}
    """
    # Precompile regexes up-front for performance
    try:
        compiled_rules: Dict[str, Tuple[Pattern[str], Any]] = {
            key: (re.compile(regex), default)
            for key, (regex, default) in extraction_rules.items()
        }
    except re.error as err:
        crawl_logger.error(
            f"Error when precompiling the regex to capture property values from filename. "
            f"Check regex patterns. Error details: {err}"
        )
        raise

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Optional[Artefact]:
            filename = kwargs["filename"]
            if "artefact_candidate" not in kwargs:
                kwargs["artefact_candidate"] = Artefact()

            for key, (regex, default) in compiled_rules.items():
                match = regex.search(filename)
                if match:
                    value = match.group(1)
                    kwargs["artefact_candidate"][key] = value
                else:
                    value = default
                    if value or add_none:
                        kwargs["artefact_candidate"][key] = value

            return func(*args, **kwargs)

        return wrapper

    return decorator


def _splitall(path: str) -> List[str]:
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path:  # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts


def _get_artefacts_from_folder(
    folder_path: str, functor: Callable, root_path: str
) -> Dict[str, Optional[Artefact]]:
    """Helper function that crawls all files in the given folder by calling a functor on each one.

    :param folder_path: Path to the folder to scan
    :type folder_path: str
    :param functor: Function to call for each file found. Should accept path_parts, filename, and full_path
    :type functor: Callable
    :param root_path: Root path of the crawling operation for calculating relative paths
    :type root_path: str
    :return: Dictionary mapping full file paths to artefacts (or None if file was filtered out)
    :rtype: Dict[str, Optional[Artefact]]
    """
    relative_path = os.path.relpath(folder_path, root_path)
    path_parts = _splitall(relative_path) if relative_path != "." else []
    artefacts: Dict[str, Optional[Artefact]] = {}

    try:
        with os.scandir(folder_path) as entries:
            for entry in entries:
                if entry.is_file():
                    full_path = entry.path

                    artefact = functor(
                        path_parts=path_parts, filename=entry.name, full_path=full_path
                    )

                    if artefact and not artefact[ArtefactProps.INVALID]:
                        # If invalidity is not set already assume it is false in context of crawling,
                        # since the file exists (otherwise we wouldn't have found it)
                        artefact[ArtefactProps.INVALID] = False

                    artefacts[full_path] = artefact
    except OSError as e:
        crawl_logger.warning(f"Error accessing folder {folder_path}: {e}")

    return artefacts


def _scan_directories(
    dir_path: str,
    break_checker_delegate: Optional[Callable[[os.DirEntry], bool]] = None,
) -> Generator[str, None, None]:
    """Generator that recursively scans directories using DirEntry for optimal performance.

    This function yields directory paths in a depth-first manner, using os.scandir
    for maximum performance when traversing large directory trees.

    :param dir_path: Path to start scanning from
    :param break_checker_delegate: Optional function to control directory scanning.
        Called for each directory entry. If it returns True, scanning stops for that directory.
    :yields: Directory paths as strings
    """
    # also put the starting directory on the stack
    stack = [dir_path]

    # Localize frequently-used names to speed up inner loop
    _os_scandir = os.scandir
    _break_checker_delegate = break_checker_delegate

    while stack:
        current = stack.pop()
        yield current

        try:
            it = _os_scandir(current)  # returns an iterator/ScandirIterator
        except (OSError, PermissionError) as e:
            crawl_logger.warning(f"Cannot access directory {current}: {e}")
            continue

        try:
            for entry in it:
                if _break_checker_delegate and _break_checker_delegate(entry):
                    break

                if entry.is_dir():
                    # only build child path for directories (fewer string creations)
                    stack.append(entry.path)
        finally:
            # ensure scandir iterator is closed promptly
            try:
                it.close()
            except Exception:
                pass


class DirectoryCrawler(object):
    """Helper class that crawls a directory tree starting from the given rootPath.

    The crawler assumes that every file found is a potential artefact and calls
    the provided file functor to interpret each file. If the functor returns an
    artefact, it is added to the result collection. Crawling is distributed to
    multiple parallel processes for improved performance on large directory trees.

    :param root_path: Path to the root directory. All subdirectories will be recursively crawled.
    :param file_functor: A callable or factory for callables which processes each file.
        If file_functor is a factory, a new callable will be generated for each subdirectory.
    :param replace_existing_artefacts: If True, newly found artefacts will overwrite similar
        existing ones. If False, duplicates will be dropped.
    :param n_processes: Number of parallel processes to use for crawling
    :param scan_directory_break_delegate: Optional delegate to control directory scanning.
        Called for each directory entry - if it returns True, scanning stops for that directory.
    :type scan_directory_break_delegate: Optional[Callable[[os.DirEntry], bool]]

    Example break delegate for DICOM optimization::

        def dicom_break_delegate(path: os.DirEntry) -> bool:
            # Stop scanning subdirs if we found a .dcm file (assumes one series per folder)
            return os.path.isfile(path) and path.endswith('.dcm')
    """

    def __init__(
        self,
        root_path: Union[str, os.PathLike],
        file_functor: Union[Callable, Callable[[], Callable]],
        replace_existing_artefacts: bool = False,
        n_processes: int = 1,
        scan_directory_break_delegate: Optional[Callable[[os.DirEntry], bool]] = None,
    ):

        self._rootPath: str = os.fspath(root_path)
        self._fileFunctor = file_functor
        self._replace_existing_artefacts = replace_existing_artefacts
        self._n_processes = n_processes
        self._scan_directory_break_delegate = scan_directory_break_delegate

        self._last_irrelevant = 0
        self._last_dropped = 0
        self._last_overwrites = 0
        self._last_added = 0

        # Determine if functor is a factory (callable that returns callable)
        self._functor_is_factory = False
        try:
            functor_test = self._fileFunctor()
            self._functor_is_factory = callable(functor_test)
        except Exception as err:
            crawl_logger.debug(
                f"Error when probing file_functor for being a factory. "
                f"Assuming it is a normal function. Error details: {err}"
            )

    @property
    def number_of_last_irrelevant(self):
        """Returns the number of irrelevant files (not ended up in artefats) of the last crawl."""
        return self._last_irrelevant

    @property
    def number_of_last_dropped(self):
        """Returns the number of artefacts that were dropped due to being duplicates to already found artefacts
        in the last crawl."""
        return self._last_dropped

    @property
    def number_of_last_added(self):
        """Returns the number of artefacts that were finally added in the last crawl (and not overwritten or dropped)
        So that is the number of artefacts finally in the list."""
        return self._last_added

    @property
    def number_of_last_overwites(self):
        """Returns the number of artefacts that were overwritten by simelar artefact in the cause of crawling."""
        return self._last_overwrites

    def getArtefacts(self) -> ArtefactCollection:
        """Execute the crawling operation and return collected artefacts.

        This method orchestrates the entire crawling process:
        1. Scans directories to find all folders to process
        2. Distributes folder processing across multiple processes
        3. Collects and merges results while handling duplicates
        4. Updates internal statistics

        :return: Collection of all discovered artefacts
        :raises OSError: If root directory cannot be accessed
        """
        artefacts = ArtefactCollection()
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=self._n_processes
        ) as executor, Progress(transient=True, refresh_per_second=2) as progress:
            directory_scanning = progress.add_task("Found folders to scan")
            futures = []
            for target_dir in _scan_directories(
                dir_path=self._rootPath,
                break_checker_delegate=self._scan_directory_break_delegate,
            ):
                if self._functor_is_factory:
                    functor = self._fileFunctor()
                else:
                    functor = self._fileFunctor
                progress.update(directory_scanning, advance=1)
                future = executor.submit(
                    _get_artefacts_from_folder, target_dir, functor, self._rootPath
                )
                futures.append(future)

            progress.console.print(
                f"\nDiscovered {len(futures)} directories to analyze. Starting file analysis..."
            )

            directory_analysis = progress.add_task(
                "Processing directories", total=len(futures)
            )

            self._last_irrelevant = 0
            self._last_dropped = 0
            self._last_added = 0
            self._last_overwrites = 0

            for future in concurrent.futures.as_completed(futures):
                try:
                    folder_artefacts = future.result()
                    for fullpath, artefact in folder_artefacts.items():
                        if artefact is None:
                            self._last_irrelevant += 1
                        elif (
                            not self._replace_existing_artefacts
                            and artefacts.similar_artefact_exists(artefact)
                        ):
                            self._last_dropped += 1
                        else:
                            replaced_artefact = artefacts.add_artefact(artefact)
                            if replaced_artefact:
                                self._last_overwrites += 1
                            else:
                                self._last_added += 1

                except Exception as e:
                    crawl_logger.error(f"Error processing directory results: {e}")

                progress.update(directory_analysis, advance=1)

        return artefacts


def runCrawlerScriptMain(
    file_function: Callable,
    scan_directory_break_delegate: Optional[Callable[[os.DirEntry], bool]] = None,
) -> None:
    """Helper function for creating crawler scripts with command line interface.

    This function provides a standard CLI interface for crawler scripts that need to
    crawl a root directory and store results to a file. It handles argument parsing
    and provides common options for crawler configuration.

    :param file_function: Function to call for each file found during crawling.
        Should at least accept path_parts, filename, and full_path as keyword arguments or swallow them as **kwargs.
    :param scan_directory_break_delegate: Optional delegate to control directory scanning
    :raises SystemExit: On argument parsing errors or crawling failures

    Command line arguments::

        script.py <root_dir> <output_file> [--n_processes N] [--relative_paths] [--replace]

        root_dir: Directory to start crawling from
        output_file: XML file to save discovered artefacts to
        --n_processes: Number of parallel processes (default: 1)
        --relative_paths: Store paths relative to output file location
        --replace: Replace existing similar artefacts during crawling
    """
    parser = argparse.ArgumentParser(
        description="AVID artefact crawler script for indexing files as artefacts.",
    )

    parser.add_argument(
        "root",
        help="Path to the root directory where the crawler should start scanning.",
    )
    parser.add_argument(
        "output",
        help="File path where discovered artefacts will be saved as XML. "
        "Existing files will be overwritten.",
    )

    parser.add_argument(
        "--n_processes",
        help="Number of processes for parallel folder crawling",
        default=1,
        type=int,
    )
    parser.add_argument(
        "--relative_paths",
        action="store_true",
        help="Store artefact file paths relative to the output file location",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Replace existing artefacts when similar ones are found in the same crawl",
    )

    try:
        cliargs, unknown = parser.parse_known_args()
    except SystemExit:
        raise

    if not os.path.exists(cliargs.root):
        crawl_logger.error(f"Root directory does not exist: {cliargs.root}")
        sys.exit(1)

    if not os.path.isdir(cliargs.root):
        crawl_logger.error(f"Root path is not a directory: {cliargs.root}")
        sys.exit(1)

    if cliargs.n_processes < 1:
        crawl_logger.error("Number of processes must be at least 1")
        sys.exit(1)

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(os.path.abspath(cliargs.output))
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            crawl_logger.info(f"Created output directory: {output_dir}")
        except OSError as e:
            crawl_logger.error(f"Cannot create output directory {output_dir}: {e}")
            sys.exit(1)

    # Execute crawling operation
    try:
        crawler = DirectoryCrawler(
            root_path=cliargs.root,
            file_functor=file_function,
            n_processes=cliargs.n_processes,
            replace_existing_artefacts=cliargs.replace,
            scan_directory_break_delegate=scan_directory_break_delegate,
        )
        artefacts = crawler.getArtefacts()

        console = Console()
        console.print(
            f"\n[bold]Crawling Results Summary[/bold]\n"
            f"Final artefacts collected: [green]{len(artefacts)}[/green]\n"
            f"Dropped duplicate artefacts: [yellow]{crawler.number_of_last_dropped}[/yellow]\n"
            f"Overwritten artefacts: [red]{crawler.number_of_last_overwites}[/red]\n"
            f"Irrelevant files skipped: [dim]{crawler.number_of_last_irrelevant}[/dim]\n"
        )

        crawl_logger.info(f"Saving {len(artefacts)} artefacts to {cliargs.output}...")
        saveArtefactList(
            filePath=cliargs.output,
            artefacts=artefacts,
            savePathsRelative=cliargs.relative_paths,
        )

        console.print(
            f"Successfully saved artefacts to: [green]{cliargs.output}[/green]\n"
        )

    except KeyboardInterrupt:
        crawl_logger.info("Crawling interrupted by user")
        sys.exit(130)  # Standard exit code for SIGINT
    except Exception as e:
        crawl_logger.error(f"Crawling failed with error: {e}")
        sys.exit(1)
