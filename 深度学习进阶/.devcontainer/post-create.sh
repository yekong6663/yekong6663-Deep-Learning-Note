#!/usr/bin/env bash
set -euo pipefail

# The workspace is mounted by Dev Containers as remoteUser.
mkdir -p "${PWD}/data"

bash .devcontainer/download_d2l_notebooks.sh
python .devcontainer/verify_environment.py
