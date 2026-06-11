#!/usr/bin/env python3
"""
cms.py — Cloud Management System
================================
A menu-driven console application that manages VirtualBox virtual machines and
Docker images/containers from a single, user-friendly interface.

Run it with:

    python3 cms.py

Mini-project for Cloud Computing and Networking.
"""

import sys

import utils
import docker_manager as dock
import vm_manager as vm

MENU = """
  ---------------- Cloud Management System ----------------
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
  ---------------------------------------------------------"""

# Maps each menu choice to the function that handles it.
ACTIONS = {
    "1": vm.create_vm_interactive,
    "2": vm.create_vm_from_config,
    "3": dock.create_dockerfile,
    "4": dock.build_image,
    "5": dock.list_images,
    "6": dock.list_containers,
    "7": dock.stop_container,
    "8": dock.search_local_image,
    "9": dock.search_dockerhub,
    "10": dock.pull_image,
}


def _startup_check() -> None:
    """Report which back-ends are available so the user knows what works."""
    utils.info("Docker: " + ("available" if utils.docker_available() else "NOT found"))
    vbox = utils.find_vboxmanage()
    utils.info("VirtualBox: " + (f"available ({vbox})" if vbox else "NOT found"))


def main() -> None:
    utils.header("Welcome to the Cloud Management System")
    _startup_check()

    while True:
        print(MENU)
        choice = input("  Select an option: ").strip()

        if choice == "0":
            utils.info("Goodbye!")
            break

        action = ACTIONS.get(choice)
        if action is None:
            utils.warn("Invalid option. Please choose a number from the menu.")
            continue

        try:
            action()
        except KeyboardInterrupt:
            print()
            utils.warn("Operation cancelled.")
        except Exception as exc:  # last-resort guard so the menu never crashes
            utils.error(f"Unexpected error: {exc}")

        utils.pause()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print()
        utils.info("Interrupted. Exiting.")
        sys.exit(0)
