"""Host adb fallback when Appium mobile: shell is unavailable in the session."""

from __future__ import annotations

import os
import subprocess
from typing import Sequence


def device_udid(explicit: str | None = None) -> str | None:
    return explicit or os.environ.get("ANDROID_UDID") or os.environ.get("APPIUM_UDID")


def run_adb(
    *args: str,
    udid: str | None = None,
    timeout: float = 30,
) -> tuple[bool, str]:
    """
    Run adb on the host. Returns (success, combined stdout/stderr).
    """
    serial = device_udid(udid)
    cmd: list[str] = ["adb"]
    if serial:
        cmd.extend(["-s", serial])
    cmd.extend(args)
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode == 0, out.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return False, repr(exc)


def shell(command: str, *args: str, udid: str | None = None) -> tuple[bool, str]:
    """adb shell <command> [args...]"""
    return run_adb("shell", command, *args, udid=udid)


def broadcast_am(args: Sequence[str], *, udid: str | None = None) -> tuple[bool, str]:
    """adb shell am <args...>"""
    return shell("am", *args, udid=udid)


def input_text(text: str, *, udid: str | None = None) -> tuple[bool, str]:
    """
    Type into the focused field via adb (field must be focused from Appium click).
    Spaces must be encoded as %s for adb input.
    """
    escaped = text.replace(" ", "%s")
    return shell("input", "text", escaped, udid=udid)
