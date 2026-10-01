#!/usr/bin/env bash
# Run OWASP Dependency-Check in Docker via the same Maven plugin version
# declared in pom.xml (org.owasp:dependency-check-maven:11.1.1).
# Copies HTML + JSON reports to evidencias/local/dependency-check/.
#
# Requires the NVD_API_KEY environment variable: without a key the NVD
# download takes more than 30 minutes.
#
# The named volume devsecops-maven-cache persists the Maven dependencies and
# the dependency-check NVD database (it lives inside the local Maven repo),
# so re-runs are fast.
#
# -DfailBuildOnCVSS=11 disables the plugin's own build failure (no CVSS
# score reaches 11): the quality gate reads the report and decides.
set -Eeuo pipefail

if [[ -z "${NVD_API_KEY:-}" ]]; then
  echo "[DEPENDENCY-CHECK] ERROR: NVD_API_KEY is not set." >&2
  echo "[DEPENDENCY-CHECK] Get one at https://nvd.nist.gov/developers/request-an-api-key" >&2
  echo "[DEPENDENCY-CHECK] Without a key the NVD update takes more than 30 minutes." >&2
  exit 1
fi

REPORT_DIR="evidencias/local/dependency-check"

mkdir -p "${REPORT_DIR}"

echo "[DEPENDENCY-CHECK] Scanning dependencies in Docker (this may take a while)..."

docker run --rm \
  -v "$PWD:/workspace" \
  -w /workspace \
  -v devsecops-maven-cache:/root/.m2/repository \
  -e NVD_API_KEY \
  maven:3.9-eclipse-temurin-21 \
  mvn -B org.owasp:dependency-check-maven:11.1.1:check \
    -DnvdApiKey="${NVD_API_KEY}" \
    -DfailBuildOnCVSS=11 \
    -Dformat='HTML,JSON'

for report in dependency-check-report.html dependency-check-report.json; do
  if [[ -f "target/${report}" ]]; then
    cp "target/${report}" "${REPORT_DIR}/${report}"
    echo "[DEPENDENCY-CHECK] Report generated: ${REPORT_DIR}/${report}"
  else
    echo "[DEPENDENCY-CHECK] ERROR: expected report not found: target/${report}" >&2
    exit 1
  fi
done

echo "[DEPENDENCY-CHECK] Done (plugin gate disabled via failBuildOnCVSS=11; the quality gate decides)."
