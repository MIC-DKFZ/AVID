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

import sys
import traceback
import re
from typing import Any, Optional, TextIO, Union
import time

# Try to import rich components, set flags for availability
try:
    from rich.console import Console as RichConsole
    from rich.table import Table as RichTable
    from rich.traceback import Traceback as RichTraceback
    from rich.panel import Panel as RichPanel
    from rich.columns import Columns as RichColumns
    from rich.padding import Padding as RichPadding
    from rich.progress import Progress as RichProgress
    from rich.logging import RichHandler
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

RICH_TAG_PATTERN = re.compile(
        r'\[/?(?:'
        r'[a-zA-Z_][\w-]*'  # tag name like bold, red, underline
        r'(?:=[^\]]+)?'  # optional =something
        r'(?:\s+[a-zA-Z_][\w-]*(?:=[^\]]+)?)*)'  # optional additional attributes
        r'\]'
    )


def _test_for_limited_encoding():
    return sys.stdout.encoding == 'cp1252'

ONLY_LIMITED_ENCODING_IS_SUPPORTED = _test_for_limited_encoding()

#only use rich if it is there and the environment supports rich encoding (e.g utf8)
RICH_AVAILABLE = RICH_AVAILABLE and not ONLY_LIMITED_ENCODING_IS_SUPPORTED

class ConsoleTable:
    """Abstraction for table creation that works with or without rich"""

    def __init__(self, title: Optional[str] = None):
        self.title = title
        self.columns = []
        self.rows = []

    def add_column(self, header: str, justify: str = "left"):
        self.columns.append({"header": header, "justify": justify})

    def add_row(self, *values):
        self.rows.append(values)


class ConsolePanel:
    """Abstraction for panel creation that works with or without rich"""

    def __init__(self, content: Any, title: Optional[str] = None):
        self.content = content
        self.title = title

    def __str__(self):
        return f"Panel(title={self.title})"

    def __repr__(self):
        return f"ConsolePanel(content={repr(self.content)}, title={self.title})"


class ConsoleColumns:
    """Abstraction for column layout that works with or without rich"""

    def __init__(self, renderables):
        # Ensure renderables is always a list/tuple
        if not isinstance(renderables, (list, tuple)):
            self.renderables = [renderables]
        else:
            self.renderables = renderables

    def __str__(self):
        return f"Columns({len(self.renderables)} items)"

    def __repr__(self):
        return f"ConsoleColumns(renderables={repr(self.renderables)})"


class ConsolePadding:
    """Abstraction for padding that works with or without rich"""

    def __init__(self, renderable, pad: tuple = (0, 0, 0, 0)):
        self.renderable = renderable
        self.pad = pad


class ConsoleTraceback:
    """Abstraction for traceback formatting that works with or without rich"""

    def __init__(self, exc_type, exc_value, exc_traceback):
        self.exc_type = exc_type
        self.exc_value = exc_value
        self.exc_traceback = exc_traceback

    @classmethod
    def from_exception(cls, exc_type, exc_value, exc_traceback):
        return cls(exc_type, exc_value, exc_traceback)


if RICH_AVAILABLE:
    TableType = RichTable
    PanelType = RichPanel
    ColumnsType = RichColumns
    PaddingType = RichPadding
    TracebackType = RichTraceback
else:
    TableType = ConsoleTable
    PanelType = ConsolePanel
    ColumnsType = ConsoleColumns
    PaddingType = ConsolePadding
    TracebackType = ConsoleTraceback


class Console:
    """
    Console abstraction that uses rich if available, falls back to simple stdout otherwise.
    Provides a subset of rich.Console functionality with graceful degradation.
    """

    @staticmethod
    def __force_jupyter():
        """Helper function that checks if we are running in a IPython or jupyter environment."""
        try:
            from IPython import get_ipython
            shell = get_ipython().__class__.__name__
            if shell == "ZMQInteractiveShell":
                return True  # Jupyter notebook or qtconsole
            elif shell == "TerminalInteractiveShell":
                return None  # IPython in terminal
            else:
                return None  # Other (maybe colab, etc.)
        except Exception:
            return None

    def __init__(self, file: Optional[TextIO] = None, width: Optional[int] = None):
        self.file = file or sys.stdout
        self.width = width
        self._rich_console = None

        if RICH_AVAILABLE:
            self._rich_console = RichConsole(file=self.file, width=width, force_jupyter=Console.__force_jupyter())

    @property
    def is_terminal(self) -> bool:
        """Check if output is going to a terminal"""
        if self._rich_console:
            return self._rich_console.is_terminal
        return hasattr(self.file, 'isatty') and self.file.isatty()

    def print(self, *objects, sep: str = " ", end: str = "\n", style: Optional[str] = None, **kwargs):
        """Print objects to the console with optional styling"""
        if self._rich_console:
            # Use rich console if available
            self._rich_console.print(*objects, sep=sep, end=end, style=style, **kwargs)
        else:
            # Fallback to simple print, strip rich markup and handle nested objects
            cleaned_objects = []
            for obj in objects:
                cleaned_objects.append(self._process_object_recursive(obj))
            print(*cleaned_objects, sep=sep, end=end, file=self.file, **kwargs)

    def rule(self, title: Optional[str] = None, characters: str = "─", style: Optional[str] = None):
        """Print a horizontal rule"""
        if self._rich_console:
            self._rich_console.rule(title, characters=characters, style=style)
        else:
            # Simple fallback rule
            width = 80  # Default width for fallback
            if title:
                rule_text = f" {title} "
                padding = (width - len(rule_text)) // 2
                line = characters * padding + rule_text + characters * padding
                if len(line) < width:
                    line += characters * (width - len(line))
            else:
                line = characters * width
            print(line, file=self.file)

    def _process_object_recursive(self, obj) -> str:
        """Recursively process objects, handling nested rich components"""
        if isinstance(obj, (ConsoleTable, ConsolePanel, ConsoleColumns, ConsolePadding, ConsoleTraceback)):
            return self._render_simple(obj)
        elif isinstance(obj, str):
            return self._strip_markup(obj)
        elif isinstance(obj, (list, tuple)):
            # Handle lists/tuples of objects (common in columns)
            processed_items = [self._process_object_recursive(item) for item in obj]
            return " | ".join(processed_items)
        elif hasattr(obj, '__rich__') or hasattr(obj, '__rich_console__'):
            # Handle other rich objects by converting to string and stripping markup
            return self._strip_markup(str(obj))
        else:
            return str(obj)

    def _strip_markup(self, text: str) -> str:
        """Remove rich markup from text for plain output"""
        return RICH_TAG_PATTERN.sub('', str(text))

    def _render_simple(self, obj) -> str:
        """Render objects in simple text format"""
        if isinstance(obj, ConsoleTable):
            return self._render_table_simple(obj)
        elif isinstance(obj, ConsolePanel):
            return self._render_panel_simple(obj)
        elif isinstance(obj, ConsoleColumns):
            return self._render_columns_simple(obj)
        elif isinstance(obj, ConsolePadding):
            return self._render_padding_simple(obj)
        elif isinstance(obj, ConsoleTraceback):
            return self._render_traceback_simple(obj)
        else:
            return self._process_object_recursive(obj)

    def _render_table_simple(self, table: ConsoleTable) -> str:
        """Render table in simple text format"""
        result = []
        if table.title:
            result.append(f"\n{table.title.upper()}\n" + "=" * len(table.title))

        if table.columns and table.rows:
            # Calculate column widths
            headers = [col["header"] for col in table.columns]
            widths = [len(header) for header in headers]

            for row in table.rows:
                for i, cell in enumerate(row):
                    if i < len(widths):
                        widths[i] = max(widths[i], len(str(cell)))

            # Print header
            header_row = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
            result.append(header_row)
            result.append("-" * len(header_row))

            # Print rows
            for row in table.rows:
                row_str = " | ".join(str(cell).ljust(widths[i]) if i < len(widths) else str(cell)
                                     for i, cell in enumerate(row))
                result.append(row_str)

        return "\n".join(result)

    def _render_panel_simple(self, panel: ConsolePanel) -> str:
        """Render panel in simple text format"""
        content = self._process_object_recursive(panel.content)
        if panel.title:
            title_line = f"--- {panel.title} ---"
            separator = "-" * len(title_line)
            return f"\n{title_line}\n{content}\n{separator}"
        return f"\n{content}\n"

    def _render_columns_simple(self, columns: ConsoleColumns) -> str:
        """Render columns in simple text format"""
        processed_items = []
        for item in columns.renderables:
            processed_items.append(self._process_object_recursive(item))
        return " | ".join(processed_items)

    def _render_padding_simple(self, padding: ConsolePadding) -> str:
        """Render padding in simple text format"""
        content = self._process_object_recursive(padding.renderable)

        # Apply simple padding (just add spaces/newlines based on pad values)
        top, right, bottom, left = padding.pad

        # Add top padding (newlines)
        result = "\n" * top

        # Add left padding and content
        if left > 0:
            lines = content.split('\n')
            padded_lines = [" " * left + line for line in lines]
            result += '\n'.join(padded_lines)
        else:
            result += content

        # Add bottom padding (newlines)
        result += "\n" * bottom

        return result

    def _render_traceback_simple(self, tb: ConsoleTraceback) -> str:
        """Render traceback in simple text format"""
        return ''.join(traceback.format_exception(tb.exc_type, tb.exc_value, tb.exc_traceback))


class Progress:
    """Progress abstraction that uses rich if available, provides simple fallback otherwise"""

    def __init__(self, console: Optional[Console] = None, transient: bool = False, refresh_per_second: float = 10):
        self.console = console or Console()
        self.transient = transient
        self._refresh_per_second = refresh_per_second
        self._refresh_wait_in_seconds = 1/refresh_per_second
        self._rich_progress = None
        self._tasks = {}
        self._task_counter = 0
        self._last_display_lines = 0

        if RICH_AVAILABLE and self.console._rich_console:
            self._rich_progress = RichProgress(console=self.console._rich_console, transient=transient,
                                               refresh_per_second=refresh_per_second)

    def add_task(self, description: str, total: Optional[int] = None, indicator_cadence: Optional[float] = None) -> int:
        """
        Add a progress task
        :return: ID of the task that should be updated.
        :param description: the task label.
        :param total: the value that indicates 100\% of progress. If None the end of the task is not known.
        :param indicator_cadence: Used for action state indication in none terminal modes. It is the amount of
        advancement needed before a new state update will be printed in a new line. That is used to control
        the amount of output in file like outputs (like stdout).
        """
        task_id = self._task_counter
        self._task_counter += 1

        if self._rich_progress:
            real_task_id = self._rich_progress.add_task(description, total=total)
            self._tasks[task_id] = {
                'rich_id': real_task_id,
                'description': description,
                'total': total,
                'completed': 0,
                'start_time':time.time(),
                'indicator_cadence': indicator_cadence
            }
        else:
            self._tasks[task_id] = {
                'description': description,
                'total': total,
                'completed': 0,
                'start_time':time.time(),
                'last_update_time': 0,
                'indicator_cadence': indicator_cadence
            }

        return task_id

    def update(self, task_id: int, advance: Optional[float] = None, total: Optional[float] = None,
               completed: Optional[float] = None, indicator_cadence: Optional[float] = None, **kwargs):
        """Update progress for a task
        :param task_id: ID of the task that should be updated.
        :param advance: Increment of the progress. If None is passed the progress will not be changed but other
        values will be updated.
        :param total: the value that indicates 100\% of progress. If None the end of the task is not known.
        :param indicator_cadence: Used for action state indication in none terminal modes. It is the amount of
        advancement needed before a new state update will be printed in a new line. That is used to control
        the amount of output in file like outputs (like stdout).
        """
        if task_id not in self._tasks:
            return

        task = self._tasks[task_id]

        if total:
            task["total"] = total

        if indicator_cadence:
            task["indicator_cadence"] = indicator_cadence

        old_complete = task.get("completed", 0)
        if advance:
            task["completed"] += advance

        if completed:
            task["completed"] = completed
        new_complete = task.get("completed", 0)

        has_completed_now = old_complete < new_complete and task.get('total', None)\
                            and new_complete >= task.get('total', 0)

        if self._rich_progress and "rich_id" in task and self.console.is_terminal:
            self._rich_progress.update(task["rich_id"], advance=advance, total=total, completed=completed, **kwargs)
        else:
            # Simple progress with visual bar and time estimates
            current_time = time.time()

            # Only update display every _refresh_wait_in_seconds seconds to avoid flickering,
            # except it was just completed
            if not has_completed_now\
                    and current_time - task.get("last_update_time", 0) < self._refresh_wait_in_seconds:
                return

            task["last_update_time"] = current_time

            if self.console.is_terminal:
                self._display_all_tasks()
            else:
                # it is an action based progress in a non terminal, thus we indicate the progress with explicit
                # print-outs in non rich mode
                current_interval = None
                if task['indicator_cadence']:
                    current_interval = round(task["completed"]/task['indicator_cadence'])

                if has_completed_now or current_interval is None or ('current_interval' not in task or task['current_interval'] != current_interval):
                    task['current_interval'] = current_interval
                    progress_line = self._format_progress_line(task)
                    self.console.print(f"\n{progress_line}  ", end='')
                if 'action_state_indicator' in kwargs:
                    self.console.print(f"{kwargs['action_state_indicator']}", end='')

    def refresh(self):
        """Force a refresh of the progress display (like flush)."""
        if self._rich_progress:
            self._rich_progress.refresh()
        else:
            self._display_all_tasks()

    def stop(self):
        """Stop the progress display and render a final state."""
        if self._rich_progress:
            self._rich_progress.stop()
        else:
            self._display_all_tasks()
            task_completed = 0
            for taskid, task in self._tasks.items():
                total = task.get('total')
                if not total:
                    total = 0
                if task.get('completed', 0) >= total:
                    task_completed += 1
            self.console.print(f"Progress stopped. {task_completed} tasks completed.")

    def _display_all_tasks(self):
        """Display all active tasks in a block, updating the entire display"""
        # Move cursor up to overwrite previous display
        if self._last_display_lines > 0:
            # Move cursor up and clear lines
            for _ in range(self._last_display_lines):
                self.console.print(f"\033[A\033[K", end='')  # Move up one line and clear it
        else:
            #first time tasks are displayed in current setup. Move to new  line
            #to avoid overriding last other line
            self.console.print('\n')

        # Display each task
        lines_displayed = 0
        for task_id in self._tasks:
            task = self._tasks[task_id]
            progress_line = self._format_progress_line(task)
            self.console.print(progress_line)
            lines_displayed += 1

        self._last_display_lines = lines_displayed

        # Ensure we flush to see the update immediately
        if hasattr(self.console.file, 'flush'):
            self.console.file.flush()

    def _format_progress_line(self, task: dict) -> str:
        """Format a single progress line for a task"""
        description = task["description"]
        completed = task["completed"]
        total = task.get("total")
        start_time = task["start_time"]
        current_time = time.time()

        elapsed = current_time - start_time
        if total and total<=completed:
            if 'elapsed_time' in task:
                elapsed = task['elapsed_time']
            else:
                task['elapsed_time'] = elapsed

        if total and total > 0:
            # Calculate percentage and create visual bar
            percentage = min((completed / total) * 100, 100)
            bar_width = 30
            filled_width = int((percentage / 100) * bar_width)

            if ONLY_LIMITED_ENCODING_IS_SUPPORTED:
                bar = "#" * filled_width + " " * (bar_width - filled_width)
            else:
                bar = "█" * filled_width + "░" * (bar_width - filled_width)

            # Calculate time estimates
            time_info = self._format_time_estimates(completed, total, elapsed)

            # Format: Description [████████░░░░] 45.2% (123/456) - 2m 15s elapsed, ~3m 45s remaining
            return f"{description} [{bar}] {percentage:5.1f}% ({int(completed)}/{int(total)}) - {time_info}"
        else:
            # Indeterminate progress - show spinner and count
            if ONLY_LIMITED_ENCODING_IS_SUPPORTED:
                spinner_chars = r"/-\|"
            else:
                spinner_chars = r"◐◓◑◒"

            spinner_idx = int(current_time * 10) % len(spinner_chars)
            spinner = spinner_chars[spinner_idx]

            elapsed_str = self._format_duration(elapsed)
            return f"{description} {spinner} {int(completed)} items - {elapsed_str} elapsed"

    def _format_time_estimates(self, completed: float, total: float, elapsed: float) -> str:
        """Format time estimates for progress display"""
        elapsed_str = self._format_duration(elapsed)
        if completed <= 0 or elapsed <= 0:
            return f"{elapsed_str} elapsed"

        # Calculate rate and remaining time
        rate = completed / elapsed
        remaining_items = total - completed

        if rate > 0:
            eta_seconds = remaining_items / rate
            eta_str = self._format_duration(eta_seconds)
            return f"{elapsed_str} elapsed, ~{eta_str} remaining"
        else:
            return f"{elapsed_str} elapsed"

    def _format_duration(self, seconds: float) -> str:
        """Format duration in a human-readable format"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"

    def __enter__(self):
        if self._rich_progress:
            self._rich_progress.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._rich_progress:
            self._rich_progress.__exit__(exc_type, exc_val, exc_tb)
        else:
            self.stop()


def inspect(obj, console: Optional[Console] = None, private: bool = False, docs: bool = True):
    """Inspect an object, with rich formatting if available"""
    console = console or Console()

    if RICH_AVAILABLE and console._rich_console:
        from rich import inspect as rich_inspect
        rich_inspect(obj, console=console._rich_console, private=private, docs=docs)
    else:
        # Simple fallback inspection
        import inspect as py_inspect
        console.print(f"Object: {obj}")
        console.print(f"Type: {type(obj)}")
        if hasattr(obj, '__dict__'):
            console.print("Attributes:")
            for name, value in obj.__dict__.items():
                if not private and name.startswith('_'):
                    continue
                console.print(f"  {name}: {value}")


def get_logging_handler(level=None):
    """Get appropriate logging handler based on rich availability"""
    if RICH_AVAILABLE:
        handler = RichHandler(level=level)
    else:
        import logging
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)-8s [%(levelname)s] %(message)s')
        handler.setFormatter(formatter)

    if level:
        handler.setLevel(level)
    return handler


# Factory functions to create objects with the right backend
def create_table(title: Optional[str] = None) -> TableType:
    """Create a table object using rich if available, fallback otherwise"""
    if RICH_AVAILABLE:
        return RichTable(title=title)
    return ConsoleTable(title=title)


def create_panel(content: Any, title: Optional[str] = None) -> PanelType:
    """Create a panel object using rich if available, fallback otherwise"""
    if RICH_AVAILABLE:
        return RichPanel(content, title=title)
    return ConsolePanel(content, title=title)


def create_columns(renderables) -> ColumnsType:
    """Create a columns object using rich if available, fallback otherwise"""
    if RICH_AVAILABLE:
        return RichColumns(renderables)
    return ConsoleColumns(renderables)


def create_padding(renderable, pad: tuple = (0, 0, 0, 0)) -> PaddingType:
    """Create a padding object using rich if available, fallback otherwise"""
    if RICH_AVAILABLE:
        return RichPadding(renderable, pad=pad)
    return ConsolePadding(renderable, pad=pad)


def create_traceback_from_exception(exc_type, exc_value, exc_traceback) -> TracebackType:
    """Create a traceback object using rich if available, fallback otherwise"""
    if RICH_AVAILABLE:
        return RichTraceback.from_exception(exc_type, exc_value, exc_traceback)
    return ConsoleTraceback.from_exception(exc_type, exc_value, exc_traceback)


def is_rich_object(obj) -> bool:
    """Check if an object is a rich-compatible object"""
    if RICH_AVAILABLE:
        # Check for rich objects
        rich_types = (RichTable, RichPanel, RichColumns, RichPadding, RichTraceback)
        if isinstance(obj, rich_types):
            return True

    # Check for our abstraction objects
    abstraction_types = (ConsoleTable, ConsolePanel, ConsoleColumns, ConsolePadding, ConsoleTraceback)
    return isinstance(obj, abstraction_types)
