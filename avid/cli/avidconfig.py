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

from __future__ import annotations

import argparse
import configparser
import platform
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from urllib.request import urlretrieve

from avid.common.console_abstraction import Console, TableType, PrettyType, ConfirmType, PromptType, Progress

import avid.common.config_manager as cfg
import avid.common.AVIDUrlLocater as loc

console = Console()


def _parse_cli_value(val: str):
    """Convert CLI arg string into int/float/bool if possible. Used to generate setting values from CLI arg"""
    if val.lower() in ("true", "yes", "on"):
        return True
    if val.lower() in ("false", "no", "off"):
        return False
    try:
        return int(val)
    except ValueError:
        pass
    try:
        return float(val)
    except ValueError:
        pass
    return val


# -----------------------
# Package & tool installation
# -----------------------
def get_all_known_packages() -> List[str]:
    """Return list of known package names that this installer understands."""
    return ["MITK"]


def _get_os_name() -> str:
    return platform.system()


def download_with_progress(url: str, dest: Path) -> None:
    """Download a file with progress bar."""
    progress = Progress()
    task_id = progress.add_task("Progress", total=100)

    def hook(blocks_transferred: int, block_size: int, total_size: int):
        if total_size > 0:
            downloaded = blocks_transferred * block_size
            percent = min(downloaded / total_size * 100, 100)
            progress.update(task_id, completed=percent)

    with progress:
        urlretrieve(url, dest, reporthook=hook)

def get_and_unpack_mitk(mitk_source_config_path: Path, packages_path: Path, update: bool = False) -> Path:
    """
    Download and unpack MITK package based on the sources.config for the current OS.

    Returns: path to unpacked MITK directory (inside packages_path / 'MITK')
    """
    cp = configparser.ConfigParser()
    cp.read(str(mitk_source_config_path))

    mitk_dir = packages_path / "MITK"
    if mitk_dir.exists():
        if update:
            shutil.rmtree(mitk_dir)
        else:
            raise RuntimeError("MITK already present in package directory. Use update mode to replace it.")

    os_name = _get_os_name()
    try:
        url = cp.get(os_name, "url")
    except Exception:
        url = None

    if url is None:
        raise RuntimeError("No MITK download found for the current OS. Check the package sources.config")

    filename = url.split("/")[-1]
    filepath = packages_path / filename
    console.print(f"Downloading [cyan]MITK[/] from [blue]{url}[/] to [yellow]{filepath}[/] ...")
    download_with_progress(url, filepath)

    if os_name == "Windows":
        with zipfile.ZipFile(str(filepath), "r") as zip_f:
            zip_f.extractall(str(packages_path))
        # assume archive created folder named like filename without .zip
        extracted_dir = packages_path / filename[:-4]
        if extracted_dir.exists():
            extracted_dir.rename(mitk_dir)

    elif os_name == "Linux":
        with tarfile.open(str(filepath), "r:gz") as tar_f:
            tar_f.extractall(str(packages_path))
        extracted_dir = packages_path / filename[:-7]  # .tar.gz
        if extracted_dir.exists():
            extracted_dir.rename(mitk_dir)

    elif os_name == "Darwin":
        import dmglib
        # MITK has a license that needs to be confirmed when mounting, so we need to send a "yes"
        subprocess.run("yes | PAGER=cat hdiutil attach " + filepath, shell=True)
        try:
            for mount_point in dmglib.dmg_get_mountpoints(filepath):
                shutil.copytree(str(Path(mount_point) / "MitkWorkbench.app"), mitk_dir)
        finally:
            dmglib.dmg_detach_already_attached(filepath)

    # cleanup downloaded file
    try:
        filepath.unlink()
    except Exception:
        pass

    return mitk_dir


def install_tool_from_package(tool_name: str, package_name: str, package_path: Path, scope: str) -> None:
    """
    Install a single tool from a package.
    Writes the tool config (avid_tool_config.toml) into the tools_root/tool-configs/<tool_name>/ directory.
    """
    # read package tools config (INI)
    package_tools_config = loc.get_tool_package_tools_config_path(package_name)
    cp = configparser.ConfigParser()
    cp.read(str(package_tools_config))

    console.print(f"Installing tool [bold]{tool_name}[/] from package [cyan]{package_name}[/] ...")
    exec_path = None

    if package_name == "MITK":
        try:
            mitk_exec_name = cp.get(tool_name, "executableName")
        except Exception:
            mitk_exec_name = None

        os_name = _get_os_name()
        if mitk_exec_name:
            if os_name == "Windows":
                exec_path = package_path / "apps" / (mitk_exec_name + ".bat")
            elif os_name == "Linux":
                exec_path = package_path / "apps" / (mitk_exec_name + ".sh")
            elif os_name == "Darwin":
                exec_path = package_path / "Contents" / "MacOS" / mitk_exec_name
    else:
        console.print(f"[red]No installer logic for package [cyan]{package_name}[/][/]")
        return

    if exec_path is None:
        console.print(f"[red]Executable for [bold white]{tool_name}[/] not provided in package metadata.[/]\n"
                      f"Make sure your tool is correctly set up in the tools-sources.config.")
        return

    if not exec_path.is_file():
        console.print(f"[red]Executable [yellow]{exec_path}[/] not found. Aborting install for [bold white]{tool_name}"
                      f"[/].[/]\n"
                      "Please make sure you are using the correct path and a current version of "
                      "the package.")
        return

    target_cfg_path = cfg.get_venv_tool_config_file_path(tool_id=tool_name) if scope == cfg.SCOPE_VENV\
        else cfg.get_user_tool_config_file_path(tool_id=tool_name)

    if target_cfg_path is None:
        console.print(f"[red]Could not determine tool config path for [bold white]{tool_name}[/][/]")
        return

    target_cfg_path.parent.mkdir(parents=True, exist_ok=True)
    toml_dict = {}
    cfg.set_setting_in_dict(cfg.TOOL_SETTING_NAMES.DEFAULT_EXECUTABLE_PATH, toml_dict, str(exec_path))
    cfg._save_toml(target_cfg_path, toml_dict)

    console.print(f"[green]Tool {tool_name} installed.[/] Config written to [yellow]{target_cfg_path}[/]")


def install_package(package_name: str, scope: str, local_package_path: Optional[Path] = None) -> None:
    """
    Install a package (e.g. MITK). If local_package_path is provided, use it instead of downloading.
    """

    tools_root_dir = cfg.get_venv_tools_default_root_dir() if scope == cfg.SCOPE_VENV else cfg.get_user_tools_default_root_dir()
    if tools_root_dir is None:
        console.print("[red]Could not determine tools root for selected scope[/]")
        return

    tools_root_dir.mkdir(parents=True, exist_ok=True)

    packages_dir = tools_root_dir / "packages"
    packages_dir.mkdir(parents=True, exist_ok=True)

    package_path = None

    console.print(f"Changed scope: {'[magenta]venv[/]' if scope==cfg.SCOPE_VENV else '[cyan]user[/]'}")

    if package_name == "MITK":
        if local_package_path:
            package_path = Path(local_package_path)
            if not package_path.exists():
                console.print(f"[red]Provided local package path does not exist: [yellow]{package_path}[/][/]")
                return
        else:
            try:
                mitk_sources = loc.get_tool_package_source_config_path("MITK")
            except Exception as exc:
                console.print(f"[red]Cannot find MITK sources.config:[/] {exc}")
                return
            package_path = get_and_unpack_mitk(mitk_sources, packages_dir, update=False)

    else:
        console.print(f"[red]Unknown package [cyan]{package_name}[/]; skipping.[/]")
        return

    # install tools listed in package's tools.config
    try:
        package_tools_cfg = loc.get_tool_package_tools_config_path(package_name)
    except Exception as exc:
        console.print(f"[red]Cannot find package tools config for [cyan]{package_name}[/][/]: {exc}")
        return

    cp = configparser.ConfigParser()
    cp.read(str(package_tools_cfg))
    for tool_name in cp.sections():
        install_tool_from_package(tool_name, package_name=package_name, package_path=package_path, scope=scope)


# -----------------------
# CLI command handlers
# -----------------------
def cmd_package_install(args: argparse.Namespace, scope: str) -> None:
    """Install package(s) into the chosen scope/tools root."""
    packages = list(args.packages or [])
    local_package_path_str = getattr(args, "localPackagePath", None)
    local_package_path = Path(local_package_path_str) if local_package_path_str else None

    if len(packages) != 1 and local_package_path:
        console.print("[red]Error. For command argument '--localPackagePath', a single package name must be specified.[/red]")
        return

    if not packages:
        # install all known packages after confirmation
        known = get_all_known_packages()
        console.print(f"No package specified. Known packages: {known}")
        if not ConfirmType.ask("Install all known packages?", default=True):
            console.print("Aborted.")
            return
        packages = known

    for package in packages:
        try:
            install_package(package, scope=scope, local_package_path=local_package_path)
        except Exception as exc:
            console.print(f"[red]Failed to install {package}: {exc}[/]")


def cmd_package_list(args: argparse.Namespace, scope: str) -> None:
    """List of known an installed."""
    known_package_names = get_all_known_packages()

    if len(known_package_names) == 0:
        console.print("[yellow]No packages known.[/]")
        return

    table = TableType()
    table.add_column("Package ID")

    for package_id in known_package_names:
        table.add_row( package_id )

    console.print(table)


def cmd_tool_add(args: argparse.Namespace, scope: str) -> None:
    """Register a custom tool by writing user-scoped tool config (exe path)."""
    cfg_dict = {}
    cfg.set_setting_in_dict(cfg.TOOL_SETTING_NAMES.DEFAULT_EXECUTABLE_PATH, cfg_dict, str(args.path))

    if scope == cfg.SCOPE_VENV:
        cfg.save_venv_tool_config(args.tool_id, cfg_dict)
    else:
        cfg.save_user_tool_config(args.tool_id, cfg_dict)
    console.print(f"Changed scope: {'[magenta]venv[/]' if scope==cfg.SCOPE_VENV else '[cyan]user[/]'}")
    console.print(f"[green]Added[/] tool [green]{args.tool_id}[/] with executable path: [yellow]{args.path}[/]")
    console.print()


def cmd_tool_remove(args: argparse.Namespace, scope: str) -> None:
    """Remove tool for a tool id in the given scope."""
    if scope == cfg.SCOPE_VENV:
        tool_path = cfg.get_venv_tool_config_dir(args.tool_id)
    else:
        tool_path = cfg.get_user_tool_config_dir(args.tool_id)

    console.print(f"Changed scope: {'[magenta]venv[/]' if scope==cfg.SCOPE_VENV else '[cyan]user[/]'}")

    if tool_path and tool_path.exists():
        shutil.rmtree(tool_path)
        console.print(f"[green]Removed tool at [yellow] {tool_path}[/][/]")
    else:
        console.print(f"[red]Tool does not exist in requested scope. Nothing is removed.[/]")
    console.print()


def cmd_tool_list(args: argparse.Namespace, scope: str) -> None:
    """List installed tools across user and venv scopes."""
    user_tools = dict()
    try:
        tool_configs_path = cfg.get_user_tools_root_dir() / cfg.TOOL_CONFIGS_SUB_DIR
        if tool_configs_path.exists():
            for d in tool_configs_path.iterdir():
                if d.is_dir():
                    user_tools[d.name] = str(d)
    except Exception:
        pass
    venv_tools = dict()
    try:
        tool_configs_path = cfg.get_venv_tools_root_dir() / cfg.TOOL_CONFIGS_SUB_DIR
        if tool_configs_path and tool_configs_path.exists():
            for d in tool_configs_path.iterdir():
                if d.is_dir():
                    venv_tools[d.name] = str(d)
    except Exception:
        pass

    unique_keys = sorted(user_tools.keys() | venv_tools.keys())

    if len(unique_keys) == 0:
        console.print("[yellow]No tools installed.[/]")
        return

    table = TableType(title="Installed Tools")
    table.add_column("Tool ID")
    table.add_column("Used scope")
    table.add_column("Used path")

    for tool_id in unique_keys:
        table.add_row(
            tool_id,
            "[magenta]venv[/]" if tool_id in venv_tools is not None else "[cyan]user[/]",
            str(venv_tools[tool_id]) if tool_id in venv_tools is not None else str(user_tools[tool_id])
        )

    console.print(table)

    file_path = cfg.get_venv_tools_root_dir()
    console.print(f"Venv tools root path: [magenta]{file_path if file_path and file_path.exists() else 'N/A'}[/]")
    file_path = cfg.get_user_tools_root_dir()
    console.print(f"User tools root path: [cyan]{file_path if file_path.exists() else 'N/A'}[/]")
    console.print()


def cmd_tool_info(args: argparse.Namespace, scope: str) -> None:
    """Show active tool config (venv wins), and indicate which scope provided it."""
    tool_id = args.tool_id
    if scope == cfg.SCOPE_VENV:
        tool_cfg = cfg.load_venv_tool_config(tool_id)
    else:
        tool_cfg = cfg.load_user_tool_config(tool_id)

    if tool_cfg:
        console.print(f"Configuration info for tool [bold green]{tool_id}[/] (scope: "
                      f"{'[magenta]venv[/]' if scope==cfg.SCOPE_VENV else '[cyan]user[/]'}):\n")
        console.print(PrettyType(tool_cfg, expand_all=True))
    else:
        console.print(f"Tool [bold red]{tool_id}[/] is not installed in scope "
                      f"{'[magenta]venv[/]' if scope==cfg.SCOPE_VENV else '[cyan]user[/]'}."
                      f" No info available.")
    console.print()


def cmd_settings_list(args: argparse.Namespace, scope: str) -> None:
    """List settings."""
    console.print("AVID Settings")
    user_cfg = cfg.load_user_config()
    venv_cfg = cfg.load_venv_config()
    merged_cfg = cfg.load_merged_config()

    # Collect all keys across scopes
    keys = set()

    for d in [user_cfg, venv_cfg, merged_cfg]:
        if d:
            new_keys = cfg.collect_keys_from_config_dict(d)
            keys.update(new_keys)

    table = TableType(title="Settings (all scopes)")
    table.add_column("Key")
    table.add_column("Defaults")
    table.add_column("User", style="cyan")
    table.add_column("Venv", style="magenta")
    table.add_column("Used", style="bright_yellow")

    for key in sorted(keys):
        default_val = cfg.get_setting_from_dict(key, config_dict=cfg.DEFAULTS)
        user_val = cfg.get_setting(key, cfg.SCOPE_USER)
        venv_val = cfg.get_setting(key, cfg.SCOPE_VENV)
        merged_val = cfg.get_setting(key, cfg.SCOPE_MERGED)
        table.add_row(
            key,
            str(default_val) if default_val is not None else "-",
            str(user_val) if user_val is not None else "-",
            str(venv_val) if venv_val is not None else "-",
            str(merged_val) if merged_val is not None else "-",
        )

    console.print(table)
    file_path = cfg.get_venv_config_file_path()
    console.print(f"Venv scope location: [magenta]{file_path if file_path and file_path.exists() else 'N/A'}[/]")
    file_path = cfg.get_user_config_file_path()
    console.print(f"User scope location: [cyan]{file_path if file_path.exists() else 'N/A'}[/]")
    console.print()


def cmd_settings_get(args: argparse.Namespace, scope: str) -> None:
    """Show user, venv, and merged values for a setting."""
    key = args.key
    merged_val = cfg.get_setting(key, cfg.SCOPE_MERGED)
    user_val = cfg.get_setting(key, cfg.SCOPE_USER)
    venv_val = cfg.get_setting(key, cfg.SCOPE_VENV)
    default_val = cfg.get_setting_from_dict(key, config_dict=cfg.DEFAULTS)
    console.print(f"Setting: {key}")
    table = TableType()
    table.add_column("Scope")
    table.add_column("Value")
    table.add_row("Default", str(default_val) if default_val is not None else "-")
    table.add_row("User", f"[cyan]{user_val if user_val is not None else '-'}[/]")
    table.add_row("Venv", f"[magenta]{venv_val if venv_val is not None else '-'}[/]")
    table.add_row("Used", f"[bright_yellow]{merged_val if merged_val is not None else '-'}[/]")
    console.print(table)

    file_path = cfg.get_venv_config_file_path()
    console.print(f"Venv scope location: [magenta]{file_path if file_path and file_path.exists() else 'N/A'}[/]")
    file_path = cfg.get_user_config_file_path()
    console.print(f"User scope location: [cyan]{file_path if file_path.exists() else 'N/A'}[/]")
    console.print()


def cmd_settings_set(args: argparse.Namespace, scope: str) -> None:
    """Set a setting in the chosen scope (default behavior uses venv if available)."""
    val = _parse_cli_value(args.value)
    cfg.set_setting(args.key, val, scope)
    console.print(f"Set [green]{args.key}[/] = [bright_yellow]{val}[/]")

    console.print(f"Changed scope: {'[magenta]venv[/]' if scope==cfg.SCOPE_VENV else '[cyan]user[/]'}")
    file_path = cfg.get_venv_config_file_path() if scope == cfg.SCOPE_VENV else cfg.get_user_config_file_path()
    console.print(f"Changed config location: [yellow]{file_path}[/]")
    console.print()


def cmd_settings_unset(args: argparse.Namespace, scope: str) -> None:
    """Unset a setting in the chosen scope."""
    value_to_unset = cfg.get_setting(args.key,scope)
    if isinstance(value_to_unset, dict):
        if not ConfirmType.ask("The key is indicating a group of settings. Do you really want to delete all"
                           " sub keys?",
                           default=False):
            console.print(f"[yellow]Nothing unset.[/]")
            console.print()
            return

    was_unset = cfg.unset_setting(args.key, scope)

    if was_unset:
        console.print(f"Unset [green]{args.key}[/]")
        console.print(f"Changed scope: {'[magenta]venv[/]' if scope==cfg.SCOPE_VENV else '[cyan]user[/]'}")
        file_path = cfg.get_venv_config_file_path() if scope == cfg.SCOPE_VENV else cfg.get_user_config_file_path()
        console.print(f"Changed config location: [yellow]{file_path}[/]")
    else:
        console.print(f"[yellow]Nothing unset.[/] Specified key [green]{args.key}[/] does not exist in scope.")
        console.print(f"Checked scope: {'[magenta]venv[/]' if scope==cfg.SCOPE_VENV else '[cyan]user[/]'}")
        file_path = cfg.get_venv_config_file_path() if scope == cfg.SCOPE_VENV else cfg.get_user_config_file_path()
        console.print(f"Checked config location: [yellow]{file_path}[/]")
    console.print()


def cmd_tool_settings_set(args: argparse.Namespace, scope: str) -> None:
    """Set a value inside a tool config."""
    tool_id = args.tool_id
    key = args.key
    val = _parse_cli_value(args.value)

    if scope == cfg.SCOPE_VENV:
        active_cfg = cfg.load_venv_tool_config(tool_id)
    else:
        active_cfg = cfg.load_user_tool_config(tool_id)

    if not active_cfg:
        console.print(f"[red]Tool [white bold]{tool_id}[/] is not installed in scope "
                      f"{'[magenta]venv[/]' if scope==cfg.SCOPE_VENV else '[cyan]user[/]'}.[/]\n"
                      f" No setting changed.")
        console.print()
        return

    cfg.set_setting_in_dict(key, config_dict=active_cfg, value=val)
    if scope == cfg.SCOPE_VENV:
        cfg.save_venv_tool_config(tool_id, active_cfg)
    else:
        cfg.save_user_tool_config(tool_id, active_cfg)

    console.print(f"Set [green]{args.key}[/] = [bright_yellow]{val}[/]")
    console.print(f"Changed scope: {'[magenta]venv[/]' if scope==cfg.SCOPE_VENV else '[cyan]user[/]'}")
    file_path = cfg.get_venv_config_file_path() if scope == cfg.SCOPE_VENV else cfg.get_user_config_file_path()
    console.print(f"Changed config location: [yellow]{file_path}[/]")
    console.print()


def cmd_tool_settings_get(args: argparse.Namespace, scope: str) -> None:
    tool_id = args.tool_id
    key = args.key
    if scope == cfg.SCOPE_VENV:
        active_cfg = cfg.load_venv_tool_config(tool_id)
    else:
        active_cfg = cfg.load_user_tool_config(tool_id)

    if not active_cfg:
        console.print(f"[red]Tool [white bold]{tool_id}[/] is not installed in scope "
                      f"{'[magenta]venv[/]' if scope==cfg.SCOPE_VENV else '[cyan]user[/]'}.[/]\n"
                      f" No setting available.")
        console.print()
        return

    val = cfg.get_setting_from_dict(key, config_dict=active_cfg)
    console.print(f"Shown scope: {'[magenta]venv[/]' if scope == cfg.SCOPE_VENV else '[cyan]user[/]'}")
    if val:
        console.print(f"[green]{args.key}[/] = [bright_yellow]{val}[/]")
    else:
        console.print(f"[yellow]Not available.[/] Setting [green]{args.key}[/] does not exist for tool {tool_id} in scope.")

    console.print()


def cmd_tool_settings_unset(args: argparse.Namespace, scope: str) -> None:
    tool_id = args.tool_id
    key = args.key
    if scope == cfg.SCOPE_VENV:
        active_cfg = cfg.load_venv_tool_config(tool_id)
    else:
        active_cfg = cfg.load_user_tool_config(tool_id)

    if not active_cfg:
        console.print(f"[red]Tool [white bold]{tool_id}[/] is not installed in scope "
                      f"{'[magenta]venv[/]' if scope==cfg.SCOPE_VENV else '[cyan]user[/]'}.[/]\n"
                      f" No setting changed.")
        console.print()
        return

    value_to_unset = cfg.get_setting_from_dict(key, config_dict=active_cfg)
    if isinstance(value_to_unset, dict):
        if not ConfirmType.ask("The key is indicating a group of settings. Do you really want to delete all"
                           " sub keys?",
                           default=False):
            console.print(f"[yellow]Nothing unset.[/]")
            console.print()
            return

    was_unset = cfg.unset_setting_in_dict(key, config_dict=active_cfg)
    if scope == cfg.SCOPE_VENV:
        cfg.save_venv_tool_config(tool_id, active_cfg)
    else:
        cfg.save_user_tool_config(tool_id, active_cfg)

    if was_unset:
        console.print(f"Unset [green]{args.key}[/]")
        console.print(f"Changed scope: {'[magenta]venv[/]' if scope==cfg.SCOPE_VENV else '[cyan]user[/]'}")
        file_path = cfg.get_venv_config_file_path() if scope == cfg.SCOPE_VENV else cfg.get_user_config_file_path()
        console.print(f"Changed config location: [yellow]{file_path}[/]")
    else:
        console.print(f"[yellow]Nothing unset.[/] Specified key [green]{args.key}[/]"
                      f" does not exist for tool in scope.")
        console.print(f"Checked scope: {'[magenta]venv[/]' if scope==cfg.SCOPE_VENV else '[cyan]user[/]'}")
        file_path = cfg.get_venv_config_file_path() if scope == cfg.SCOPE_VENV else cfg.get_user_config_file_path()
        console.print(f"Checked config location: [yellow]{file_path}[/]")
    console.print()


def cmd_tool_settings_list(args: argparse.Namespace, scope: str) -> None:
    tool_id = args.tool_id
    if scope == cfg.SCOPE_VENV:
        tool_cfg = cfg.load_venv_tool_config(tool_id)
    else:
        tool_cfg = cfg.load_user_tool_config(tool_id)

    if tool_cfg:
        # Collect all keys across scopes
        keys = cfg.collect_keys_from_config_dict(tool_cfg)

        table = TableType(title="Tool settings")
        table.add_column("Key")
        table.add_column("Value", style="bright_yellow")

        for key in sorted(keys):
            val = cfg.get_setting_from_dict(key, config_dict=tool_cfg)
            table.add_row(
                key,
                str(val) if val is not None else "-",
            )

        console.print(table)
        console.print(f"Listed scope: {'[magenta]venv[/]' if scope == cfg.SCOPE_VENV else '[cyan]user[/]'}")
        file_path = cfg.get_venv_tool_config_file_path(tool_id=tool_id) if scope == cfg.SCOPE_VENV\
            else cfg.get_user_tool_config_file_path(tool_id=tool_id)
        console.print(f"Config location: [yellow]{file_path if file_path.exists() else 'N/A'}[/]")
    else:
        console.print(f"[red]Tool [white bold]{tool_id}[/] is not installed in scope "
                      f"{'[magenta]venv[/]' if scope==cfg.SCOPE_VENV else '[cyan]user[/]'}.[/]\n"
                      f" No info available.")
    console.print()


def cmd_setup(args: argparse.Namespace, scope: str) -> None:
    console.rule()
    console.print("Welcome to the [bold]AVID[/bold] setup wizard\n")
    console.print("This wizard will help you configure and setup AVID.")

    scope = cfg.SCOPE_USER
    if cfg.in_venv():
        scope = PromptType.ask("You are running in a venv.\nDo you want to configure AVID for the venv or for your user?",
                               choices=[cfg.SCOPE_VENV, cfg.SCOPE_USER], default=cfg.SCOPE_VENV)
    console.print(f"Used scope: {'[magenta]venv[/]' if scope == cfg.SCOPE_VENV else '[cyan]user[/]'}")
    cfg_path = cfg.get_user_config_file_path() if scope == cfg.SCOPE_USER else cfg.get_venv_config_file_path()
    console.print(f"Used config path: [yellow]{cfg_path}[/]\n")

    tool_path = cfg.get_user_tools_root_dir() if scope == cfg.SCOPE_USER else cfg.get_venv_tools_root_dir()

    console.print(f"Default tool root dir is: [yellow]{tool_path}[/yellow]")
    if not ConfirmType.ask("Use default tool root dir?", default=True):
        new_path = PromptType.ask("Enter custom tool root (absolute)")
        cfg.set_setting(cfg.SETTING_NAMES.TOOLS_PATH, new_path, scope)
        console.print(f"[green]Saved custom tool path:[/] [yellow]{new_path}[/]")

    console.print()

    # optional install mitk
    if ConfirmType.ask("Would you like to also install the MITK package with its tools now (ca 200 MB)?", default=True):
        args.__setattr__("packages", ["MITK"])
        cmd_package_install(args=args, scope=scope)

    console.print()
    console.print(f"[green]Setup finished. Have fun.[/]")


# -----------------------
# Parser & dispatch
# -----------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser("avidconfig")
    p.add_argument("--user", dest="scope", action="store_const", const=cfg.SCOPE_USER, help="Operate on user-level config")
    p.add_argument("--venv", dest="scope", action="store_const", const=cfg.SCOPE_VENV, help="Operate on venv-level config")
    p.set_defaults(scope=None)

    sub = p.add_subparsers(dest="command", required=True)

    # settings
    sp = sub.add_parser("settings", help="General settings")
    ssub = sp.add_subparsers(dest="subcmd")
    s_list = ssub.add_parser("list", help="List settings")
    s_list.add_argument("--details", action="store_true", help="Show all scopes + merged")
    s_list.set_defaults(func=cmd_settings_list)
    s_get = ssub.add_parser("get", help="Get a setting")
    s_get.add_argument("key", help="Key of the setting that should be queried. Supports nested keys"
                                   " (e.g. action.timeout)")
    s_get.set_defaults(func=cmd_settings_get)
    s_set = ssub.add_parser("set", help="Set a setting")
    s_set.add_argument("key", help="Key of the setting that should be changed. Supports nested keys"
                                   " (e.g. action.timeout)")
    s_set.add_argument("value")
    s_set.set_defaults(func=cmd_settings_set)
    s_unset = ssub.add_parser("unset", help="Remove a setting")
    s_unset.add_argument("key", help="Key of the setting that should be removed. Supports nested keys"
                                   " (e.g. action.timeout)")
    s_unset.set_defaults(func=cmd_settings_unset)

    # package (install, list)
    pp = sub.add_parser("package", help="Tool package management")
    psub = pp.add_subparsers(dest="subcmd")
    p_install = psub.add_parser("install", help="Install package(s) (e.g. MITK)")
    p_install.add_argument("packages", nargs="*", help="Package names to install")
    p_install.add_argument("--localPackagePath", help="Use local package path instead of downloading")
    p_install.set_defaults(func=cmd_package_install)

    p_list = psub.add_parser("list", help="List of packages")
    p_list.set_defaults(func=cmd_package_list)

    # tool (add/remove/list/info)
    tp = sub.add_parser("tool", help="Tool package and tool management")
    tsub = tp.add_subparsers(dest="subcmd")
    t_add = tsub.add_parser("add", help="Add a custom tool")
    t_add.add_argument("tool_id")
    t_add.add_argument("path")
    t_add.set_defaults(func=cmd_tool_add)

    t_rm = tsub.add_parser("remove", help="Remove a tool")
    t_rm.add_argument("tool_id")
    t_rm.set_defaults(func=cmd_tool_remove)

    t_list = tsub.add_parser("list", help="List installed tools")
    t_list.set_defaults(func=cmd_tool_list)

    t_info = tsub.add_parser("info", help="Show tool information")
    t_info.add_argument("tool_id")
    t_info.set_defaults(func=cmd_tool_info)

    # tool-settings
    tsp = sub.add_parser("tool-settings", help="Tool-specific settings")
    tssub = tsp.add_subparsers(dest="subcmd")

    ts_set = tssub.add_parser("set", help="Set tool setting")
    ts_set.add_argument("tool_id", help="Tool identifier")
    ts_set.add_argument("key", help="Setting key (e.g. timeout or ui.theme)")
    ts_set.add_argument("value", help="Value")
    ts_set.set_defaults(func=cmd_tool_settings_set)

    ts_get = tssub.add_parser("get", help="Get tool setting")
    ts_get.add_argument("tool_id")
    ts_get.add_argument("key")
    ts_get.set_defaults(func=cmd_tool_settings_get)

    ts_unset = tssub.add_parser("unset", help="Unset tool setting")
    ts_unset.add_argument("tool_id")
    ts_unset.add_argument("key")
    ts_unset.set_defaults(func=cmd_tool_settings_unset)

    ts_list = tssub.add_parser("list", help="List tool settings")
    ts_list.add_argument("tool_id")
    ts_list.set_defaults(func=cmd_tool_settings_list)

    # setup wizard
    setup = sub.add_parser("setup", help="Interactive first-time setup")
    setup.set_defaults(func=cmd_setup)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    parse_namespace = parser.parse_args(argv)
    scope = cfg.get_valid_scope(parse_namespace.scope)

    if scope == cfg.SCOPE_VENV and not cfg.in_venv():
        console.print(f"[red]Try to run avidconfig in venv scope without being in a venv[/].\n"
                      f"Activate a venv or don't use the --venv flag.")
        return 2

    # catch missing subcommands and show proper help
    sub_commands = ["settings", "package", "tool", "tool-settings"]
    for sub_command in sub_commands:
        if parse_namespace.command == sub_command and parse_namespace.subcmd is None:
            parser.parse_args([sub_command, "--help"])
            return 2

    try:
        parse_namespace.func(parse_namespace, scope)
    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
