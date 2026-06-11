# Cloud Management System — Project & Testing Report

## 1. Overview

This report describes the design of the Cloud Management System (CMS), the
challenges encountered, and the testing performed. CMS is a Python 3 console
application that manages VirtualBox VMs and Docker images/containers through a
single numbered menu.

## 2. Design choices

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Language | Python 3 | Clear menu UI, strong input validation, easy to document. |
| Dependencies | Standard library only | Nothing to `pip install`; portable and easy to grade. |
| Back-end access | Wrap the real `docker` and `VBoxManage` CLIs via `subprocess` | Transparent, matches the tools taught in the course, and the exact commands appear in the output for auditing. |
| Structure | Separate modules (`docker_manager`, `vm_manager`, `utils`, `cms`) | Separation of concerns; each feature is independently testable. |
| Config file | JSON | Standard-library parsing; simple and human-readable. |
| Interface | Numbered interactive menu | User-friendly, matches the project requirement. |

### Architecture

```
cms.py  ──►  menu loop, dispatch table
  │
  ├─►  vm_manager.py     ─► VBoxManage  (createvm, modifyvm, createmedium, storagectl, storageattach)
  ├─►  docker_manager.py ─► docker      (build, images, ps, stop, search, pull)
  └─►  utils.py          ─► run(), input validation, coloured output, VBoxManage discovery
```

### VM creation steps

1. `createvm --name <n> --ostype <t> --register`
2. `modifyvm <n> --cpus <c> --memory <m> --vram 16 --nic1 nat`
3. `createmedium disk --filename <disk.vdi> --size <mb> --format VDI`
4. `storagectl <n> --name SATA --add sata --controller IntelAhci`
5. `storageattach <n> --storagectl SATA --port 0 --device 0 --type hdd --medium <disk.vdi>`

## 3. Challenges and solutions

| Challenge | Solution |
|-----------|----------|
| **VirtualBox cannot run inside WSL2** (it is itself a VM; the `vboxdrv` kernel module will not load). | Install VirtualBox on the Windows host and call `VBoxManage.exe` from WSL via the `/mnt/c/...` path. `utils.find_vboxmanage()` auto-detects it and honours a `VBOXMANAGE` override. |
| **WSL ↔ Windows path translation** for the VM disk. | Instead of constructing paths ourselves, we read the VM's own `CfgFile` from `showvminfo --machinereadable` and place the `.vdi` beside it, reusing VirtualBox's native path string. |
| **Avoiding accidental overwrites.** | The creator checks `list vms` and refuses to create a VM whose name already exists. |
| **Robust input.** | `utils.ask` / `ask_int` re-prompt on empty or out-of-range values; the menu loop wraps every action in a try/except so it never crashes. |
| **Detecting empty local-image search results.** | `docker images <ref>` always prints a header; we treat "header only, no rows" as no match. |

## 4. Test environment

- OS: Linux (WSL2) — `6.6.87.2-microsoft-standard-WSL2`
- Docker: `29.1.3`
- VirtualBox: `7.2.8` (Windows host, reached via `VBoxManage.exe`)
- Python: `3.13`

## 5. Test cases

| # | Feature | Input | Expected | Result |
|---|---------|-------|----------|--------|
| T1 | List images (5) | — | Table of local images | **Pass** |
| T2 | Create Dockerfile (3) | dir `/tmp/cmstest`, busybox content | File written | **Pass** |
| T3 | Build image (4) | `/tmp/cmstest/Dockerfile`, `cms-demo:1.0` | Image built | **Pass** |
| T4 | Search local (8) | `cms-demo` | Shows `cms-demo:1.0` | **Pass** |
| T5 | Search Docker Hub (9) | `hello-world` | Lists Hub results | **Pass** |
| T6 | Pull image (10) | `hello-world:latest` | Image pulled | **Pass** |
| T7 | List containers (6) | — | Shows running containers | **Pass** |
| T8 | Stop container (7) | `cms-stoptest` | Container stopped | **Pass** |
| T9 | Create VM from config (2) | `configs/vm_sample.json` | VM `demo-vm` created & registered | **Pass** |
| T10 | Duplicate-VM guard | re-run T9 | Refused with error | **Pass** |
| T11 | Invalid menu option | `99` | "Invalid option" message | **Pass** |

### Selected evidence

**T3 — Build image**
```
Step 1/2 : FROM busybox:latest
Step 2/2 : CMD ["echo","hello from CMS"]
Successfully built c1685936f101
Successfully tagged cms-demo:1.0
[✓] Image 'cms-demo:1.0' built successfully.
```

**T8 — Stop container**
```
[i] Running: docker stop cms-stoptest
[✓] Container 'cms-stoptest' stopped.
```

**T9 — Create VM from config**
```
[i] Creating VM 'demo-vm' (2 CPU, 2048 MB RAM, 10240 MB disk, Ubuntu_64)
Virtual machine 'demo-vm' is created and registered.
UUID: 9803bfa9-106e-443a-8a11-689105fa8c2d
Medium created. UUID: 9ef37f34-fb8d-4976-8d94-09137b4430d8
[✓] VM 'demo-vm' created and configured successfully.
```
Host verification (`VBoxManage showvminfo demo-vm --machinereadable`):
```
name="demo-vm"
ostype="Ubuntu (64-bit)"
memory=2048
cpus=2
"SATA-0-0"="C:\Users\user\VirtualBox VMs\demo-vm\demo-vm.vdi"
```

**T10 — Duplicate-VM guard**
```
[✗] A VM named 'demo-vm' already exists. Choose another name.
```

## 6. Evaluation

All eleven test cases passed. Each Docker feature was exercised against a live
Docker daemon, and VM creation was verified against a real VirtualBox 7.2.8
host, including confirmation of the VM's CPU, memory, OS type and attached
disk. Input validation, error handling and the duplicate-name guard behaved as
designed.

> Note: screenshots from the grader's own machine (the menu, a built image, and
> the VM appearing in the VirtualBox GUI) can be added here as final visual
> evidence for submission.

## 7. Possible future work

- Additional VM operations (start/stop/delete, attach ISO).
- Container start/remove and image delete.
- YAML config support and batch creation of multiple VMs.
