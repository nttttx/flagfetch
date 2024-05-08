#!/usr/bin/env python3
"""Flagfetch source code"""

from pathlib import Path
from shutil import which
import sys
import platform

# Settings
## Used to print debug output.
DEBUG = False
## Separator is used to separate flags.
SEPARATOR = " | "
FLAG_LINE_BEGIN = " + "


# Source code begins here.
def debug(to_print):
    """Prints any data to stderr if DEBUG variable is set.

    Args:
        to_print: Data to print. Should be any string
    """
    if DEBUG:
        sys.stderr.write(to_print + "\n")


def _get_distro_name():
    """Returns current distribution name using /etc/os-release file
    Returns:
        str: Host's distribution name.
        None: When platform.freedesktop_os_release() raises Exception
              or when PRETTY_NAME key is missing.
    """

    try:
        os_release = platform.freedesktop_os_release()
        distro_name = os_release["PRETTY_NAME"]
    except (OSError, KeyError):
        return None
    return distro_name


def _get_init_system():
    """Returns init system.
    Init system is identified by searching for it's management executables.

    Returns:
        str: Init system name.
        None: When nothing was found.
    """

    INITTAB = Path("/etc/inittab")
    BSD_RC = Path("/etc/rc")
    DETECTABLE = {
        "systemctl": "SystemD",
        "rc-status": "OpenRC",
        "dinitctl": "Dinit",
        "runsv": "runit",
        "herd": "GNU Shepherd",
    }

    for executable_name, init_system_name in DETECTABLE.items():
        debug(f"Checking {executable_name}: {init_system_name}")
        if which(executable_name):
            return init_system_name

    debug(f"Checking for SysV's {INITTAB}")
    if INITTAB.exists():
        return "SysV Style Init"

    debug(f"Checking for BSD's {BSD_RC}")
    if BSD_RC.exists():
        return "BSD Style Init"

    debug("Giving up trying to determine the init system. None")
    return None


def _booted_using_EFI():
    """Returns if system was booted using EFI or BIOS
    Basically checks if /sys/firmware/efi exists

    Returns:
        bool: system was booted using EFI
    """

    efi_fw_exists = Path("/sys/firmware/efi").exists()

    debug(f"efi: {efi_fw_exists}")
    return efi_fw_exists


def _check_usr_linkage():
    """Checks if /lib appears to be a symlink to /usr/lib.
    For additional information: www.freedesktop.org/wiki/Software/systemd/TheCaseForTheUsrMerge

    Returns:
        bool: /lib is symlink to /usr/lib
    """

    lib_is_symlink = Path("/lib").is_symlink()
    debug(f"/lib is a symlink: {lib_is_symlink}")

    return lib_is_symlink


def _linux():
    """Runs when system appears to be linux.
    """
    dirty_flags = [
        _get_distro_name(),
        _get_init_system(),
        "EFI" if _booted_using_EFI() else None,
        "Merged usr" if _check_usr_linkage() else "Split usr",
    ]

    clean_flags = list(
        filter(lambda item: item is not None, dirty_flags)
    )

    print(FLAG_LINE_BEGIN + SEPARATOR.join(clean_flags))


def _darwin():
    raise NotImplementedError


def _windows():
    raise NotImplementedError


def print_hardware_flags():
    raise NotImplementedError

def print_software_flags():
    system = platform.uname().system
    print(system)
    if system == "Linux":
        _linux()



def main():
    print_software_flags()


if __name__ == "__main__":
    main()
