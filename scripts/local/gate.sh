#!/usr/bin/env bash
# Run the local quality gate over the reports in evidencias/local/.
# Short command on purpose: it reads well in screenshots and logs.
set -Eeuo pipefail
cd "$(dirname "$0")/../.."

python3 scripts/quality_gate.py \
  --semgrep evidencias/local/semgrep/semgrep-results.json \
  --spotbugs evidencias/local/spotbugs/spotbugsXml.xml \
  --dependency-check evidencias/local/dependency-check/dependency-check-report.json
