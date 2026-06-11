"""
vm_manager.py
-------------
Virtual-machine feature of the Cloud Management System (objective 1):
create a VirtualBox VM from either interactive input or a configuration file.

The VM configuration accepts: name, CPU count, memory (MB), disk size (MB)
and OS type. Creation is done through the VBoxManage CLI in four steps:

    1. createvm     -> register an empty VM
    2. modifyvm     -> set CPU / memory / network
    3. createmedium -> create a virtual hard disk (.vdi)
    4. storagectl + storageattach -> attach the disk via a SATA controller

When running under WSL the VBoxManage.exe binary on the Windows host is used,
so paths returned by VirtualBox are Windows paths and are handled as such.
"""

import json
import os

import utils

DEFAULT_OSTYPE = "Linux_64"


def _vbox():
    """Locate VBoxManage or report a helpful error."""
    path = utils.find_vboxmanage()
    if path is None:
        utils.error(
            "VBoxManage was not found.\n"
            "    - Install VirtualBox, or\n"
            "    - set the VBOXMANAGE environment variable to its full path.\n"
            "    (Under WSL this is usually "
            "/mnt/c/Program Files/Oracle/VirtualBox/VBoxManage.exe)"
        )
    return path


def _disk_path_for(vbox: str, name: str):
    """Return the disk path to use for VM `name`, based on its config folder.

    We read the VM's CfgFile (the .vbox file) via showvminfo and place the
    .vdi next to it. This keeps the disk inside the VM's own folder and avoids
    any WSL<->Windows path translation, because we reuse the exact path string
    VirtualBox itself reports.
    """
    result = utils.run(
        [vbox, "showvminfo", name, "--machinereadable"],
        capture=True,
        show_cmd=False,
    )
    cfg_file = None
    for line in (result.stdout or "").splitlines():
        if line.startswith("CfgFile="):
            cfg_file = line.split("=", 1)[1].strip().strip('"')
            break
    if not cfg_file:
        return None

    # CfgFile looks like  C:\Users\me\VirtualBox VMs\demo\demo.vbox
    # Use the native separator of that path (backslash on Windows hosts).
    sep = "\\" if "\\" in cfg_file else "/"
    folder = cfg_file.rsplit(sep, 1)[0]
    return f"{folder}{sep}{name}.vdi"


def _create(name: str, cpus: int, memory_mb: int, disk_mb: int, ostype: str) -> bool:
    """Core creation routine shared by interactive and file-based flows."""
    vbox = _vbox()
    if vbox is None:
        return False

    # Refuse to clobber an existing VM of the same name.
    existing = utils.run([vbox, "list", "vms"], capture=True, show_cmd=False)
    if f'"{name}"' in (existing.stdout or ""):
        utils.error(f"A VM named '{name}' already exists. Choose another name.")
        return False

    utils.info(f"Creating VM '{name}' "
               f"({cpus} CPU, {memory_mb} MB RAM, {disk_mb} MB disk, {ostype})")

    # 1. Register the VM.
    if utils.run([vbox, "createvm", "--name", name,
                  "--ostype", ostype, "--register"]).returncode != 0:
        utils.error("createvm failed.")
        return False

    # 2. Set CPU / memory / a NAT network adapter.
    if utils.run([vbox, "modifyvm", name,
                  "--cpus", str(cpus),
                  "--memory", str(memory_mb),
                  "--vram", "16",
                  "--nic1", "nat"]).returncode != 0:
        utils.error("modifyvm failed.")
        return False

    # 3. Create the virtual hard disk.
    disk = _disk_path_for(vbox, name)
    if disk is None:
        utils.error("Could not determine the VM folder for the disk.")
        return False
    if utils.run([vbox, "createmedium", "disk",
                  "--filename", disk,
                  "--size", str(disk_mb),
                  "--format", "VDI"]).returncode != 0:
        utils.error("createmedium failed.")
        return False

    # 4. Add a SATA controller and attach the disk.
    if utils.run([vbox, "storagectl", name,
                  "--name", "SATA",
                  "--add", "sata",
                  "--controller", "IntelAhci"]).returncode != 0:
        utils.error("storagectl failed.")
        return False
    if utils.run([vbox, "storageattach", name,
                  "--storagectl", "SATA",
                  "--port", "0", "--device", "0",
                  "--type", "hdd", "--medium", disk]).returncode != 0:
        utils.error("storageattach failed.")
        return False

    utils.success(f"VM '{name}' created and configured successfully.")
    utils.info("Tip: attach an installer ISO and run "
               f"\"VBoxManage startvm {name}\" to boot it.")
    return True


# --------------------------------------------------------------------------- #
# Interactive flow                                                            #
# --------------------------------------------------------------------------- #
def create_vm_interactive() -> None:
    utils.header("Create a Virtual Machine (interactive)")
    if _vbox() is None:
        return

    name = utils.ask("VM name")
    cpus = utils.ask_int("Number of CPUs", default=1, minimum=1, maximum=32)
    memory = utils.ask_int("Memory in MB", default=2048, minimum=4)
    disk = utils.ask_int("Disk size in MB", default=10240, minimum=1)
    ostype = utils.ask("OS type (VBoxManage 'list ostypes' for options)",
                       default=DEFAULT_OSTYPE)

    _create(name, cpus, memory, disk, ostype)


# --------------------------------------------------------------------------- #
# Config-file flow                                                            #
# --------------------------------------------------------------------------- #
def create_vm_from_config(path: str = None) -> None:
    utils.header("Create a Virtual Machine (from config file)")
    if _vbox() is None:
        return

    if path is None:
        path = utils.ask("Path to the JSON config file",
                         default="configs/vm_sample.json")
    path = os.path.expanduser(path)

    if not os.path.isfile(path):
        utils.error(f"Config file not found: {path}")
        return

    try:
        with open(path) as fh:
            cfg = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        utils.error(f"Could not read/parse config: {exc}")
        return

    try:
        name = str(cfg["name"])
        cpus = int(cfg.get("cpus", 1))
        memory = int(cfg.get("memory_mb", 2048))
        disk = int(cfg.get("disk_mb", 10240))
        ostype = str(cfg.get("ostype", DEFAULT_OSTYPE))
    except (KeyError, ValueError, TypeError) as exc:
        utils.error(f"Invalid config (need at least 'name'): {exc}")
        return

    _create(name, cpus, memory, disk, ostype)
