#!/usr/bin/env bash
# Build the assignment evidence PDF in Docker (python:3.12-slim + fpdf2).
# Embeds textual evidence files and every PNG present in evidencias/capturas/.
# Output: evidencias/TP-DevSecOps-evidencias.pdf
set -Eeuo pipefail

cd "$(dirname "$0")/../.."

docker run --rm \
  -v "$PWD:/work" -w /work \
  python:3.12-slim \
  bash -c "pip install --quiet fpdf2 && python3 scripts/pdf_builder.py"

echo "[PDF] Generated: evidencias/TP-DevSecOps-evidencias.pdf"
