# Cloud Management System — User Manual

## 1. Introduction

The Cloud Management System (CMS) is a console application that lets you manage
**VirtualBox virtual machines** and **Docker images and containers** from one
simple, numbered menu. It is written in Python 3 and uses only the standard
library, so there is nothing extra to install for the program itself.

## 2. Prerequisites

| Requirement | Notes |
|-------------|-------|
| Python 3   | `python3 --version` |
| Docker      | Must be installed and your user added to the `docker` group |
| VirtualBox  | Needed only for VM features. Under WSL2, install it on Windows |

## 3. Starting the program

```bash
cd lab
python3 cms.py
```

On startup CMS prints whether Docker and VirtualBox were detected, then shows
the main menu:

```
   Virtual Machines (VirtualBox)
     1) Create a VM  (interactive input)
     2) Create a VM  (from config file)
   Docker
     3) Create a Dockerfile
     4) Build a Docker image
     5) List Docker images
     6) List running containers
     7) Stop a container
     8) Search a local image
     9) Search Docker Hub
    10) Pull an image from Docker Hub
     0) Exit
```

Type the number of the option you want and press **Enter**.

## 4. Feature guide

### Option 1 — Create a VM (interactive)
Prompts you for: VM **name**, **CPU** count, **memory** (MB), **disk size**
(MB) and **OS type**. Defaults are offered in brackets — press Enter to accept.
CMS then creates the VM, a virtual disk, and attaches the disk via a SATA
controller.

> Tip: run `VBoxManage list ostypes` to see valid OS-type identifiers
> (e.g. `Ubuntu_64`, `Windows10_64`).

### Option 2 — Create a VM (from config file)
Reads a JSON file describing the VM. Default path is
`configs/vm_sample.json`. Example:

```json
{
  "name": "demo-vm",
  "cpus": 2,
  "memory_mb": 2048,
  "disk_mb": 10240,
  "ostype": "Ubuntu_64"
}
```

Only `name` is required; other fields use defaults if omitted.

### Option 3 — Create a Dockerfile
Asks for a **directory**, a **filename** (default `Dockerfile`), then the
**contents**. Type the Dockerfile lines one per line and finish by typing a
line containing only `EOF`. Existing files are not overwritten without
confirmation.

### Option 4 — Build a Docker image
Asks for the **path to a Dockerfile** and an **image name:tag** (e.g.
`myapp:1.0`), then runs the build. The build context is the Dockerfile's
directory.

### Option 5 — List Docker images
Shows all images on the system (`docker images`).

### Option 6 — List running containers
Shows all currently running containers (`docker ps`).

### Option 7 — Stop a container
Lists running containers, then asks for a **container ID or name** to stop.

### Option 8 — Search a local image
Asks for an image **name/tag** and shows matching images already on the system.

### Option 9 — Search Docker Hub
Asks for a **name** and lists matching public images on Docker Hub, with star
counts and an "OFFICIAL" marker.

### Option 10 — Pull an image from Docker Hub
Asks for an image **name:tag** (e.g. `ubuntu:22.04`) and downloads it.

### Option 0 — Exit
Quits the program.

## 5. Error handling

CMS validates your input and reports problems clearly instead of crashing:

- Empty or out-of-range values are rejected with a re-prompt.
- Missing files (Dockerfile, config) produce a clear message.
- If Docker or VirtualBox is not available, the relevant feature explains what
  is missing instead of failing.
- Duplicate VM names are refused so you never overwrite an existing VM.

## 6. Troubleshooting

| Symptom | Cause / fix |
|---------|-------------|
| "VBoxManage was not found" | Install VirtualBox, or set the `VBOXMANAGE` env var to its full path |
| "Docker is not installed or not on PATH" | Install Docker; ensure your user is in the `docker` group |
| Docker Hub search/pull fails | Check your internet connection |
| VM disk path errors under WSL | CMS reuses VirtualBox's own reported path — make sure VirtualBox is the Windows host install |
