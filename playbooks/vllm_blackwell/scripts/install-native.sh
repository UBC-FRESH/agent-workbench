#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip wheel setuptools
python -m pip install uv
uv pip install vllm --torch-backend auto

source scripts/env-native.sh
python scripts/probe_runtime.py
