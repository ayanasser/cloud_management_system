"""
utils.py
--------
Shared helpers for the Cloud Management System (CMS):

  * running external commands (docker / VBoxManage) safely
  * locating the VirtualBox CLI (VBoxManage / VBoxManage.exe), including from WSL
  * coloured console output
  * validated interactive input

Everything here uses only the Python standard library, so the project has no
third-party dependencies to install.
"""

import os
import shutil
import subprocess
import sys

# --------------------------------------------------------------------------- #
# Coloured output                                                             #
# --------------------------------------------------------------------------- #
# ANSI colour codes are disabled automatically when the output is not a TTY
# (e.g. when piped to a file) so log captures stay clean for the report.

_USE_COLOR = sys.stdout.isatty()


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _USE_COLOR else text


def info(msg: str) -> None:
    print(_c("36", "[i] ") + msg)


def success(msg: str) -> None:
    print(_c("32", "[✓] ") + msg)


def error(msg: str) -> None:
    print(_c("31", "[✗] ") + msg)


def warn(msg: str) -> None:
    print(_c("33", "[!] ") + msg)


def header(title: str) -> None:
    line = "=" * 52
    print("\n" + _c("1;34", line))
    print(_c("1;34", f"  {title}"))
    print(_c("1;34", line))


# --------------------------------------------------------------------------- #
# Command execution                                                           #
# --------------------------------------------------------------------------- #
def run(cmd, capture: bool = False, show_cmd: bool = True):
    """Run an external command given as a list of arguments.

    Parameters
    ----------
    cmd : list[str]
        Command and arguments, e.g. ["docker", "images"].
    capture : bool
        If True, capture stdout/stderr and return them instead of streaming
        to the terminal. Used by features that need to parse output.
    show_cmd : bool
        Print the command before running it (transparency / good for the
        testing report).

    Returns
    -------
    subprocess.CompletedProcess
        Has .returncode, and (when capture=True) .stdout / .stderr.
    """
    if show_cmd:
        info("Running: " + " ".join(_quote(a) for a in cmd))
    try:
        if capture:
            return subprocess.run(cmd, text=True, capture_output=True)
        return subprocess.run(cmd, text=True)
    except FileNotFoundError:
        error(f"Command not found: {cmd[0]!r}. Is it installed and on PATH?")
        # Return a fake failed result so callers can handle it uniformly.
        return subprocess.CompletedProcess(cmd, returncode=127, stdout="", stderr="not found")


def _quote(arg: str) -> str:
    return f'"{arg}"' if " " in arg else arg


# --------------------------------------------------------------------------- #
# Tool discovery                                                              #
# --------------------------------------------------------------------------- #
def docker_available() -> bool:
    return shutil.which("docker") is not None


# Common locations for VBoxManage. When running under WSL we call the Windows
# binary on the host (/mnt/c/...). The path can be overridden with the
# VBOXMANAGE environment variable.
_VBOX_CANDIDATES = [
    "/mnt/c/Program Files/Oracle/VirtualBox/VBoxManage.exe",
    "/mnt/c/Program Files (x86)/Oracle/VirtualBox/VBoxManage.exe",
]


def find_vboxmanage():
    """Return the path to a working VBoxManage executable, or None."""
    override = os.environ.get("VBOXMANAGE")
    if override and os.path.isfile(override):
        return override
    # Native install (Linux/macOS/Windows with VBox on PATH).
    found = shutil.which("VBoxManage") or shutil.which("VBoxManage.exe")
    if found:
        return found
    # WSL -> Windows host.
    for path in _VBOX_CANDIDATES:
        if os.path.isfile(path):
            return path
    return None


# --------------------------------------------------------------------------- #
# Validated interactive input                                                 #
# --------------------------------------------------------------------------- #
def ask(prompt: str, default: str = None) -> str:
    """Ask for a non-empty string. Re-prompts until something is entered."""
    suffix = f" [{default}]" if default is not None else ""
    while True:
        value = input(f"{prompt}{suffix}: ").strip()
        if value:
            return value
        if default is not None:
            return default
        error("This value cannot be empty. Please try again.")


def ask_int(prompt: str, default: int = None, minimum: int = 1, maximum: int = None) -> int:
    """Ask for an integer within optional bounds."""
    suffix = f" [{default}]" if default is not None else ""
    while True:
        raw = input(f"{prompt}{suffix}: ").strip()
        if not raw and default is not None:
            return default
        try:
            value = int(raw)
        except ValueError:
            error("Please enter a whole number.")
            continue
        if value < minimum:
            error(f"Value must be at least {minimum}.")
            continue
        if maximum is not None and value > maximum:
            error(f"Value must be at most {maximum}.")
            continue
        return value


def confirm(prompt: str) -> bool:
    return input(f"{prompt} [y/N]: ").strip().lower() in ("y", "yes")


def pause() -> None:
    input("\nPress Enter to return to the menu...")
