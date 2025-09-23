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

"""
Central TOML-based configuration manager for AVID.

This module provides functions to manage configuration at two levels:

- **User requested_scope**: stored in the OS-specific user config/data dirs
  (via :mod:`platformdirs`).
- **Venv requested_scope**: stored under the current virtual environment root
  (``<venv>/etc/avid`` for configs, ``<venv>/var/avid`` for tools).

When loading settings, venv values always override user values
(merged view). When writing, callers can explicitly choose `user`
or `venv`. If no requested_scope is given, the default is `venv` if inside
a virtual environment, else `user`.

Tool configurations are stored in dedicated TOML files, one per tool,
located under the respective tools root (``.../tools/tool-configs/<tool-id>/avid_tool_config.toml``).
"""

# from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import toml
from platformdirs import user_config_dir, user_data_dir

APP_NAME = "avid"
APP_AUTHOR = "DKFZ"
GLOBAL_CONFIG_FILENAME = "config.toml"
TOOL_CONFIG_FILENAME = "avid_tool_config.toml"
TOOL_CONFIGS_SUB_DIR = "tool-configs"
TOOL_PACKAGES_SUB_DIR = "packages"

SCOPE_MERGED = "merged"
SCOPE_USER = "user"
SCOPE_VENV = "venv"


class SETTING_NAMES:
    ACTION_SUBPROCESS_PAUSE = "action.subprocess_pause"  # in [s]
    ACTION_TIMEOUT = "action.timeout"  # in [s]
    TOOLS_PATH = "tools_path"  # tool root path


class TOOL_SETTING_NAMES:
    DEFAULT_EXECUTABLE_PATH = (
        "default.exe"  # path of the executable in the default action config section
    )


DEFAULTS: Dict[str, Any] = {
    "action": {
        "timeout": 60,
        "subprocess_pause": 2,
    }
}

# ---------------------------------------------------------------------------
# Environment helpers
# ---------------------------------------------------------------------------


def in_venv() -> bool:
    """Return whether execution is inside a virtual environment.
    :returns: bool: True if inside a venv, False otherwise.
    """
    return sys.prefix != getattr(sys, "base_prefix", sys.prefix)


def get_valid_scope(requested_scope: Optional[str] = None) -> str:
    if requested_scope is not None:
        return requested_scope
    return SCOPE_VENV if in_venv() else SCOPE_USER


def get_user_config_dir() -> Path:
    """Return the base user configuration directory for AVID.
    Example (Linux):
        ``~/.config/avid``
    """
    return Path(user_config_dir(APP_NAME, APP_AUTHOR))


def get_user_data_dir() -> Path:
    """Return the base user data directory for AVID. This is e.g. the root where the tools path is located by default
    Example (Linux):
        ``~/.local/share/avid``
    """
    return Path(user_data_dir(APP_NAME, APP_AUTHOR))


def get_venv_root_dir() -> Optional[Path]:
    """Return the current virtual environment root, if any.
    :returns: Optional[Path]: Path to the venv root, or None if not in a venv.
    """
    return Path(sys.prefix) if in_venv() else None


def get_venv_config_dir() -> Optional[Path]:
    """Return the configuration directory for the current venv.
    Layout:
        ``<venv>/etc/avid``
    :returns: Optional[Path]: Path to venv config dir, or None if not in venv.
    """
    v = get_venv_root_dir()
    return (v / "etc" / APP_NAME) if v else None


def get_venv_data_dir() -> Optional[Path]:
    """Return the data directory for the current venv.
    Layout:
        ``<venv>/bin/avid``
    :returns: Optional[Path]: Path to venv data dir, or None if not in venv.
    """
    v = get_venv_root_dir()
    return (v / "bin" / APP_NAME) if v else None


def get_user_tools_default_root_dir() -> Path:
    """Return the default root directory for installed tools.
    Example (Linux):
        ``~/.local/share/avid/tools``
    """
    return get_user_data_dir() / "tools"


def get_venv_tools_default_root_dir() -> Optional[Path]:
    """Return the default root directory for installed tools for the current venv.
    Example (Linux):
        ``~/.local/share/avid/tools``
    """
    v = get_venv_data_dir()
    return (v / "tools") if v else None


def get_user_tools_root_dir() -> Path:
    """Return the root directory for installed tools. Either it is based on the default location or
    the setting stored in the user config file.
    """
    custom_path = get_setting(SETTING_NAMES.TOOLS_PATH, SCOPE_USER)
    return Path(custom_path) if custom_path else get_user_tools_default_root_dir()


def get_venv_tools_root_dir() -> Optional[Path]:
    """Return the root directory for installed tools for the current venv. Either it is based on the default location or
    the setting stored in the venv config file.
    """
    custom_path = get_setting(SETTING_NAMES.TOOLS_PATH, SCOPE_VENV)
    return Path(custom_path) if custom_path else get_venv_tools_default_root_dir()


def get_user_tool_config_dir(tool_id: str) -> Path:
    """Return path to a tool's config dir. Either it is based on the default location or
    the setting stored in the user config file.
    """
    return get_user_tools_root_dir() / TOOL_CONFIGS_SUB_DIR / tool_id


def get_venv_tool_config_dir(tool_id: str) -> Optional[Path]:
    """Return path to a tool's TOML config dir for the current venv. Either it is based on the default location or
    the setting stored in the venv config file.
    """
    root_dir = get_venv_tools_root_dir()
    return (root_dir / TOOL_CONFIGS_SUB_DIR / tool_id) if root_dir else None


def ensure_dir(p: Path) -> None:
    """Ensure that the given directory exists.
    :param p: Path to create.
    """
    p.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _load_toml(path: Path) -> Dict[str, Any]:
    """Load TOML file, returning empty dict if missing or invalid."""
    if not path.exists():
        return {}

    return toml.load(path)


def _save_toml(path: Path, data: Dict[str, Any]) -> None:
    """Save dictionary as TOML to file."""
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as f:
        toml.dump(data, f)


def _deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two nested dicts, values from b override a."""
    res = dict(a)
    for k, v in b.items():
        if k in res and isinstance(res[k], dict) and isinstance(v, dict):
            res[k] = _deep_merge(res[k], v)
        else:
            res[k] = v
    return res


def _get_setting_value_from_dict(
    key: str, config_dict: Dict[str, Any]
) -> Optional[Any]:
    """Retrieve a setting value.
    :param key: Dotted key, e.g. ``"core.timeout"``.
    :param scope: Indicating the scope in which the setting should be fetched.
    One of ``"user"``, ``"venv"``, ``"merged"``.
    :returns: The setting value, or None if not found.
    """
    parts = key.split(".")
    cur = config_dict
    for p in parts:
        if not isinstance(cur, dict) or p not in cur:
            return None
        cur = cur[p]
    return cur


# ---------------------------------------------------------------------------
# Config paths
# ---------------------------------------------------------------------------


def get_user_config_file_path() -> Path:
    """Return the path to the user-level config TOML file."""
    return get_user_config_dir() / GLOBAL_CONFIG_FILENAME


def get_venv_config_file_path() -> Optional[Path]:
    """Return the path to the venv-level config TOML file, if in venv."""
    v = get_venv_config_dir()
    return v / GLOBAL_CONFIG_FILENAME if v else None


def get_user_tool_config_file_path(tool_id: str) -> Path:
    """Return path to a tool's TOML config file. Either it is based on the default location or
    the setting stored in the user config file.
    """
    return get_user_tool_config_dir(tool_id) / TOOL_CONFIG_FILENAME


def get_venv_tool_config_file_path(tool_id: str) -> Optional[Path]:
    """Return path to a tool's TOML config file for the current venv. Either it is based on the default location or
    the setting stored in the venv config file.
    """
    v = get_venv_tool_config_dir(tool_id)
    return v / TOOL_CONFIG_FILENAME if v else None


# ---------------------------------------------------------------------------
# Config load/save
# ---------------------------------------------------------------------------


def load_user_config() -> Dict[str, Any]:
    """Load the user-level configuration file."""
    return _load_toml(get_user_config_file_path())


def load_venv_config() -> Dict[str, Any]:
    """Load the venv-level configuration file, if available."""
    p = get_venv_config_file_path()
    return _load_toml(p) if p else {}


def load_merged_config() -> Dict[str, Any]:
    """Load merged configuration: defaults < user < venv."""
    cfg = _deep_merge(DEFAULTS, load_user_config())
    cfg = _deep_merge(cfg, load_venv_config())
    return cfg


def save_user_config(cfg: Dict[str, Any]) -> None:
    """Write user-level config."""
    _save_toml(get_user_config_file_path(), cfg)


def save_venv_config(cfg: Dict[str, Any]) -> None:
    """Write venv-level config (error if not in venv)."""
    p = get_venv_config_file_path()
    if not p:
        raise RuntimeError("Not in a venv")
    _save_toml(p, cfg)


def collect_keys_from_config_dict(config_dict: dict[str, Any]):
    """Returns a set with all toml keys found in a dict"""
    keys: set[str] = set()

    def _iterative_collect(d: dict[str, Any], prefix: str = ""):
        for k, v in d.items():
            full_key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                _iterative_collect(v, full_key)
            else:
                keys.add(full_key)

    _iterative_collect(config_dict)
    return keys


def get_setting_from_dict(key: str, config_dict: Dict[str, Any]) -> Optional[Any]:
    """Retrieve a setting value.
    :param key: Dotted key, e.g. ``"core.timeout"``.
    :param config_dict: The loaded toml dict from which the value should be retrieved.
    :returns: The setting value, or None if not found.
    """
    parts = key.split(".")
    cur = config_dict
    for p in parts:
        if not isinstance(cur, dict) or p not in cur:
            return None
        cur = cur[p]
    return cur


def set_setting_in_dict(
    key: str, config_dict: Dict[str, Any], value: Any
) -> Optional[Any]:
    """Set a configuration value.
    :param key: Dotted key, e.g. ``"core.timeout"``.
    :param config_dict: The dict into which the value should be set.
    :param value: Setting value that should be set.
    """
    parts = key.split(".")
    cur = config_dict
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value


def unset_setting_in_dict(key: str, config_dict: Dict[str, Any]) -> bool:
    """Remove a setting. Return indicate if key was unset.
    :param key: Dotted key, e.g. ``"core.timeout"``.
    :param config_dict: The dict in which the key should be removed.
    """
    parts = key.split(".")
    cur = config_dict
    stack = []
    for p in parts[:-1]:
        if p not in cur:
            return False
        stack.append((cur, p))
        cur = cur[p]

    if parts[-1] in cur:
        cur.pop(parts[-1], None)

        for parent, pname in reversed(stack):
            if isinstance(parent[pname], dict) and not parent[pname]:
                parent.pop(pname, None)
        return True

    return False


def get_setting(key: str, scope: str = "merged") -> Optional[Any]:
    """Retrieve a setting value.
    :param key: Dotted key, e.g. ``"core.timeout"``.
    :param scope: Indicating the scope in which the setting should be fetched.
    One of ``"user"``, ``"venv"``, ``"merged"``.
    :returns: The setting value, or None if not found.
    """
    if scope == SCOPE_USER:
        cfg = load_user_config()
    elif scope == SCOPE_VENV:
        cfg = load_venv_config()
    else:
        cfg = load_merged_config()

    return get_setting_from_dict(key, config_dict=cfg)


def set_setting(key: str, value: Any, scope: Optional[str] = None) -> None:
    """Set a configuration value.
    :param key: Dotted key, e.g. ``"core.timeout"``.
    :param value: Setting value that should be set.
    :param scope: Indicating the scope in which the setting should be set.
    Valid calues are ``"user"``, ``"venv"`` or None. If None, defaults to venv when inside a venv, else user.
    """
    target = get_valid_scope(scope)
    cfg = load_venv_config() if target == SCOPE_VENV else load_user_config()

    set_setting_in_dict(key, cfg, value)

    if target == SCOPE_VENV:
        save_venv_config(cfg)
    else:
        save_user_config(cfg)


def unset_setting(key: str, scope: Optional[str] = None) -> bool:
    """Remove a setting.
    :param key: Dotted key, e.g. ``"core.timeout"``.
    :param scope: Indicating the scope in which the setting should be set.
    Valid calues are ``"user"``, ``"venv"`` or None. If None, defaults to venv when inside a venv, else user.
    """
    target = get_valid_scope(scope)
    cfg = load_venv_config() if target == SCOPE_VENV else load_user_config()

    was_unset = unset_setting_in_dict(key, cfg)

    if target == SCOPE_VENV:
        save_venv_config(cfg)
    else:
        save_user_config(cfg)

    return was_unset


# ---------------------------------------------------------------------------
# Tools config load/save
# ---------------------------------------------------------------------------


def load_user_tool_config(tool_id: str) -> Optional[Dict[str, Any]]:
    """Load the user-level tool configuration file, if available..
    :param tool_id: Tool identifier.
    :returns: toml as dict. None if the config does not exist for the passed tool id.
    """
    config_path = get_user_tool_config_file_path(tool_id=tool_id)

    return _load_toml(config_path) if config_path.exists() else None


def load_venv_tool_config(tool_id: str) -> Optional[Dict[str, Any]]:
    """Load the venv-level tool configuration file, if available..
    :param tool_id: Tool identifier.
    :returns: toml as dict. None if the config does not exist for the passed tool id.
    """
    config_path = get_venv_tool_config_file_path(tool_id=tool_id)

    return _load_toml(config_path) if config_path and config_path.exists() else None


def save_user_tool_config(tool_id: str, cfg: Dict[str, Any]) -> None:
    """Write user-level config."""
    _save_toml(get_user_tool_config_file_path(tool_id), cfg)


def save_venv_tool_config(tool_id: str, cfg: Dict[str, Any]) -> None:
    """Write venv-level config (error if not in venv)."""
    p = get_venv_tool_config_file_path(tool_id)
    if not p:
        raise RuntimeError("Not in a venv")
    _save_toml(p, cfg)
