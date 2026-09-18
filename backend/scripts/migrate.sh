#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FASTAPI_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${FASTAPI_DIR}"

# DATABASE_URL is read by alembic/env.py. The default is defined in alembic.ini.
# PYTHON_BIN can be overridden in containers or virtual environments.
PYTHON_BIN="${PYTHON_BIN:-python}"
exec "${PYTHON_BIN}" -m alembic upgrade head
