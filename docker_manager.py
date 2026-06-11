"""
docker_manager.py
-----------------
Docker-related features of the Cloud Management System (objectives 2-9):

  2. Create a Dockerfile
  3. Build a Docker image
  4. List Docker images
  5. List running containers
  6. Stop a container
  7. Search for a local image
  8. Search for an image on Docker Hub
  9. Download / pull an image from Docker Hub

Each function wraps the real `docker` CLI via utils.run() and adds input
validation and friendly error handling.
"""

import os

import utils


def _ensure_docker() -> bool:
    if not utils.docker_available():
        utils.error("Docker is not installed or not on PATH. Install Docker and retry.")
        return False
    return True


# --------------------------------------------------------------------------- #
# 2. Create a Dockerfile                                                      #
# --------------------------------------------------------------------------- #
def create_dockerfile() -> None:
    utils.header("Create a Dockerfile")
    directory = utils.ask("Directory to save the Dockerfile", default=".")
    directory = os.path.expanduser(directory)

    try:
        os.makedirs(directory, exist_ok=True)
    except OSError as exc:
        utils.error(f"Could not create directory {directory!r}: {exc}")
        return

    filename = utils.ask("Dockerfile name", default="Dockerfile")
    path = os.path.join(directory, filename)

    if os.path.exists(path) and not utils.confirm(f"{path} already exists. Overwrite?"):
        utils.warn("Aborted; existing file kept.")
        return

    print("\nEnter the Dockerfile contents line by line.")
    print("Type a single line containing only 'EOF' to finish.\n")
    lines = []
    while True:
        line = input()
        if line.strip() == "EOF":
            break
        lines.append(line)

    try:
        with open(path, "w") as fh:
            fh.write("\n".join(lines) + "\n")
    except OSError as exc:
        utils.error(f"Failed to write Dockerfile: {exc}")
        return

    utils.success(f"Dockerfile written to {os.path.abspath(path)}")


# --------------------------------------------------------------------------- #
# 3. Build a Docker image                                                     #
# --------------------------------------------------------------------------- #
def build_image() -> None:
    utils.header("Build a Docker Image")
    if not _ensure_docker():
        return

    dockerfile = utils.ask("Path to the Dockerfile", default="Dockerfile")
    dockerfile = os.path.expanduser(dockerfile)
    if not os.path.isfile(dockerfile):
        utils.error(f"Dockerfile not found: {dockerfile}")
        return

    tag = utils.ask("Image name and tag (e.g. myapp:1.0)")
    # The build context is the directory containing the Dockerfile.
    context = os.path.dirname(os.path.abspath(dockerfile)) or "."

    result = utils.run(["docker", "build", "-f", dockerfile, "-t", tag, context])
    if result.returncode == 0:
        utils.success(f"Image '{tag}' built successfully.")
    else:
        utils.error("Image build failed. Review the output above.")


# --------------------------------------------------------------------------- #
# 4. List Docker images                                                       #
# --------------------------------------------------------------------------- #
def list_images() -> None:
    utils.header("Docker Images")
    if not _ensure_docker():
        return
    utils.run(["docker", "images"])


# --------------------------------------------------------------------------- #
# 5. List running containers                                                  #
# --------------------------------------------------------------------------- #
def list_containers() -> None:
    utils.header("Running Containers")
    if not _ensure_docker():
        return
    utils.run(["docker", "ps"])


# --------------------------------------------------------------------------- #
# 6. Stop a container                                                         #
# --------------------------------------------------------------------------- #
def stop_container() -> None:
    utils.header("Stop a Container")
    if not _ensure_docker():
        return

    utils.info("Currently running containers:")
    utils.run(["docker", "ps"], show_cmd=False)

    name = utils.ask("\nContainer ID or name to stop")
    result = utils.run(["docker", "stop", name])
    if result.returncode == 0:
        utils.success(f"Container '{name}' stopped.")
    else:
        utils.error(f"Could not stop '{name}'. Check the ID/name and try again.")


# --------------------------------------------------------------------------- #
# 7. Search for a local image                                                 #
# --------------------------------------------------------------------------- #
def search_local_image() -> None:
    utils.header("Search Local Images")
    if not _ensure_docker():
        return

    term = utils.ask("Image name/tag to search for locally")
    # 'docker images <reference>' filters by repository[:tag].
    result = utils.run(["docker", "images", term], capture=True)
    output = (result.stdout or "").strip()

    # A bare header line with no rows means no match.
    if result.returncode == 0 and len(output.splitlines()) > 1:
        print(output)
        utils.success("Match(es) found above.")
    else:
        utils.warn(f"No local image matching '{term}' was found.")


# --------------------------------------------------------------------------- #
# 8. Search for an image on Docker Hub                                        #
# --------------------------------------------------------------------------- #
def search_dockerhub() -> None:
    utils.header("Search Docker Hub")
    if not _ensure_docker():
        return

    term = utils.ask("Image name to search on Docker Hub")
    result = utils.run(["docker", "search", term])
    if result.returncode != 0:
        utils.error("Docker Hub search failed (check your internet connection).")


# --------------------------------------------------------------------------- #
# 9. Pull an image from Docker Hub                                            #
# --------------------------------------------------------------------------- #
def pull_image() -> None:
    utils.header("Pull an Image from Docker Hub")
    if not _ensure_docker():
        return

    name = utils.ask("Image to pull (e.g. ubuntu:22.04)")
    result = utils.run(["docker", "pull", name])
    if result.returncode == 0:
        utils.success(f"Image '{name}' pulled successfully.")
    else:
        utils.error(f"Failed to pull '{name}'. Check the name and your connection.")
