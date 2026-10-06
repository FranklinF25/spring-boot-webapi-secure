#!/usr/bin/env bash
# Build the local-tools TP evidence PDF in Docker.
# Embeds reports/ evidence and screenshots from evidencias/capturas-tools/.
set -Eeuo pipefail
cd "$(dirname "$0")/../.."
mkdir -p evidencias/capturas-tools
docker run --rm -v "$PWD:/work" -w /work python:3.12-slim \
  bash -c "pip install --quiet fpdf2 && python3 scripts/pdf_builder_tools.py"
echo "[PDF] Generated: evidencias/TP-DevSecOps-local-tools.pdf"
