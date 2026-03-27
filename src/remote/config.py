"""Configuration persistence."""

import json
import os
import tempfile
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "tvremote"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "vizio_ip": "",
    "vizio_port": 7345,
    "vizio_auth": "",
    "cast_name": "",
    "device_type": "tv",
}


def _ensure_dir() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load() -> dict:
    if not CONFIG_FILE.exists():
        return dict(DEFAULT_CONFIG)
    try:
        with open(CONFIG_FILE) as f:
            stored = json.load(f)
    except (json.JSONDecodeError, ValueError):
        return dict(DEFAULT_CONFIG)
    merged = dict(DEFAULT_CONFIG)
    merged.update(stored)
    return merged


def save(cfg: dict) -> None:
    _ensure_dir()
    fd, tmp = tempfile.mkstemp(dir=CONFIG_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(cfg, f, indent=2)
        os.chmod(tmp, 0o600)
        os.replace(tmp, CONFIG_FILE)
    except BaseException:
        os.unlink(tmp)
        raise


def get_vizio_addr(cfg: dict) -> str:
    ip = cfg["vizio_ip"]
    port = cfg["vizio_port"]
    if not ip:
        return ""
    if ":" in str(ip):
        return str(ip)
    return f"{ip}:{port}"


def is_configured(cfg: dict) -> bool:
    return bool(cfg.get("vizio_ip") and cfg.get("vizio_auth"))
