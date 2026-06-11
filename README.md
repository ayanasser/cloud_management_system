# Cloud Management System (CMS)

A menu-driven console application that manages **VirtualBox** virtual machines
and **Docker** images/containers from a single, user-friendly interface.

Mini-project for *Cloud Computing and Networking*.

## Features

| # | Feature | Back-end |
|---|---------|----------|
| 1 | Create a VM (interactive **or** from a config file) | VirtualBox (`VBoxManage`) |
| 2 | Create a Dockerfile | filesystem |
| 3 | Build a Docker image | Docker |
| 4 | List Docker images | Docker |
| 5 | List running containers | Docker |
| 6 | Stop a container | Docker |
| 7 | Search a local image | Docker |
| 8 | Search Docker Hub | Docker |
| 9 | Pull an image from Docker Hub | Docker |

## Requirements

- **Python 3** (standard library only — no `pip install` needed)
- **Docker** installed and the user in the `docker` group
- **VirtualBox** installed (for VM features)

### Running under WSL2

VirtualBox cannot run *inside* WSL2, so install it on the **Windows host**.
The program automatically finds `VBoxManage.exe` at the default install path
(`C:\Program Files\Oracle\VirtualBox\`). To use a custom path, set:

```bash
export VBOXMANAGE="/mnt/c/path/to/VBoxManage.exe"
```

## Usage

```bash
python3 cms.py
```

Then pick options from the menu. On startup the program reports whether Docker
and VirtualBox were detected.

## Project layout

```
.
├── cms.py              # entry point + menu loop
├── docker_manager.py   # Docker features (2-9)
├── vm_manager.py       # VirtualBox VM feature (1)
├── utils.py            # shared helpers (command runner, input, output)
├── configs/
│   └── vm_sample.json  # sample VM configuration file
└── docs/
    ├── task.md
    ├── user_manual.md
    └── testing_report.md
```

## VM configuration file format

```json
{
  "name": "demo-vm",
  "cpus": 2,
  "memory_mb": 2048,
  "disk_mb": 10240,
  "ostype": "Ubuntu_64"
}
```

Only `name` is mandatory; the rest fall back to sensible defaults. Run
`VBoxManage list ostypes` to see valid `ostype` values.
# cloud_management_system
