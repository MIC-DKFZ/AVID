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
import os
import shutil
import zipfile
from tempfile import TemporaryDirectory
from pathlib import Path

from rich.table import Table
from rich.traceback import Traceback as RichTraceback
from rich import inspect as rich_inspect
from rich.console import Console
from rich.panel import Panel as RichPanel
from rich.columns import Columns as RichColumns
from rich.padding import Padding as RichPadding

from avid.common.artefact import ensureValidPath
from avid.common.osChecker import checkAndCreateDir


def print_action_diagnostics(action, console, debug=False):
    """Method that prints diagnostic information of a passed action to the passed console."""
    console.print(f'Action tag: {action.actionTag}')
    console.print(f'Action instance UID: {action.actionInstanceUID}')
    color_modifier = ''
    if action.isSuccess:
        if action.has_warnings:
            color_modifier = '[yellow]'
        else:
            color_modifier = '[green]'
    elif action.isFailure:
        color_modifier = '[red]'

    console.print(f'Status: {color_modifier}{action.last_exec_state}')

    if debug:
        console.print('Instance inspection:')
        rich_inspect(action, console=console, private=True, docs=False)

    if action.has_warnings:
        warning_panels = list()
        for (pos, warning) in enumerate(action.last_warnings):
            detail_panels = list()
            (warn_detail, exception) = warning
            detail_panels.append(f'[bold]Details:[/bold]\n{warn_detail}\n')
            if not exception is None:
                detail_panels.append('[bold]Exception:[/bold]')
                detail_panels.append(
                    RichTraceback.from_exception(exception.__class__, exception, exception.__traceback__))

            panel_title = f'Warning #{pos}'
            if action.isFailure:
                panel_title = f'Error #{pos}'

            warning_panels.append(RichPanel(RichColumns(detail_panels), title=panel_title))

        console.print('Instance warnings/errors:')
        warn_panel = RichPadding(RichColumns(warning_panels), pad=(0, 0, 0, 4))
        console.print(warn_panel)


def print_actions_overview(actions, console):
    """Method that print an overview for the provided actions."""
    table = Table(title="actions report overview")
    table.add_column("ActionTag", justify="left")
    table.add_column("UID", justify="left")
    table.add_column("State", justify="center")
    table.add_column("Warnings", justify="center")

    for action in actions:
        has_warnings = ''
        if action.has_warnings:
            has_warnings = "YES"
        table.add_row(action.actionTag,action.actionInstanceUID, action.last_exec_state, has_warnings)

    console.print(table)


def create_actions_report(actions, report_file_path, generate_report_zip=False):
    # Create a temporary directory to compile the report and collect the supplements
    with TemporaryDirectory() as temp_dir:
        checkAndCreateDir(Path(report_file_path).parent)
        temp_dir_path = Path(temp_dir)
        overview_path = temp_dir_path / 'actions_overview.txt'

        # generate the overall report for all actions
        with open(ensureValidPath(str(overview_path)), "w") as overview_file:
            diagnostic_console = Console(file=overview_file)
            print_actions_overview(actions=actions, console=diagnostic_console)

        # handle supplements
        if generate_report_zip:
            for action in actions:
                action_path = temp_dir_path / f'{action.actionTag}-{action.actionInstanceUID}'
                checkAndCreateDir(action_path)
                with open(ensureValidPath(str(action_path/'action_diagnostics.txt')), "w") as diagnostic_file:
                    diagnostic_console = Console(file=diagnostic_file)
                    print_action_diagnostics(action=action, console=diagnostic_console, debug=True)

                # now check for additional files
                try:
                    if action.last_cli_call_file_path is not None:
                        shutil.copy(action.last_cli_call_file_path,
                                    str(action_path/Path(action.last_cli_call_file_path).name))
                    if action.logFilePath is not None:
                        shutil.copy(action.logFilePath, action_path/Path(action.logFilePath).name)
                    if action.logErrorFilePath is not None:
                        shutil.copy(action.logErrorFilePath, action_path/Path(action.logErrorFilePath).name)
                except AttributeError:
                    pass

            # Create a zip file from the temporary directory structure
            with zipfile.ZipFile(report_file_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Walk through the temp directory and add files to the zip
                for root, dirs, files in os.walk(temp_dir_path):
                    for file in files:
                        file_path = Path(root) / file
                        # Add the file to the zip, maintaining the relative directory structure
                        zip_file.write(file_path, file_path.relative_to(temp_dir_path))

        else:
            shutil.copy(overview_path, report_file_path)
