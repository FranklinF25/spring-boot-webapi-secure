#!/usr/bin/env bash
# Run Semgrep in Docker, mirroring the CI SAST job (auto rules + .semgrep.yml
# over src/main/java). Writes JSON + SARIF reports to evidencias/local/semgrep/.
# The scanner never fails the build: the quality gate decides, so this script
# exits 0 as long as the analysis ran.
set -Eeuo pipefail

REPORT_DIR="evidencias/local/semgrep"
JSON_REPORT="${REPORT_DIR}/semgrep-results.json"
SARIF_REPORT="${REPORT_DIR}/semgrep-results.sarif"

mkdir -p "${REPORT_DIR}"

echo "[SEMGREP] Scanning src/main/java in Docker (config: auto + .semgrep.yml)..."

if ! docker run --rm \
    --user "$(id -u):$(id -g)" \
    -e HOME=/tmp \
    -v "$PWD:/src" \
    semgrep/semgrep:latest \
    semgrep scan \
      --config auto \
      --config .semgrep.yml \
      --metrics=on \
      --json-output="/src/${JSON_REPORT}" \
      --sarif-output="/src/${SARIF_REPORT}" \
      src/main/java; then
  echo "[SEMGREP] ERROR: Semgrep container failed, no report was produced." >&2
  exit 1
fi

echo "[SEMGREP] Reports generated:"
echo "[SEMGREP]   ${JSON_REPORT}"
echo "[SEMGREP]   ${SARIF_REPORT}"

# Findings summary by severity. Prefer jq, fall back to python3, otherwise
# just point at the JSON report.
if command -v jq >/dev/null 2>&1; then
  jq -r '.results
         | if length == 0 then "No findings"
           else group_by(.extra.severity) | .[] | "\(.[0].extra.severity): \(length)"
           end' "${JSON_REPORT}"
elif command -v python3 >/dev/null 2>&1; then
  python3 -c '
import collections, json, sys
with open(sys.argv[1], encoding="utf-8") as fh:
    data = json.load(fh)
results = data.get("results", [])
if not results:
    print("No findings")
counts = collections.Counter(
    (r.get("extra") or {}).get("severity", "UNKNOWN") for r in results
)
for severity, total in sorted(counts.items()):
    print(f"{severity}: {total}")
' "${JSON_REPORT}"
else
  echo "[SEMGREP] jq/python3 not available, see report: ${JSON_REPORT}"
fi

echo "[SEMGREP] Done (exit 0 on purpose: the quality gate decides, not the scanner)."
exit 0
