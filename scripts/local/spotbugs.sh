#!/usr/bin/env bash
# Run SpotBugs in Docker via the same Maven plugin version declared in
# pom.xml (com.github.spotbugs:spotbugs-maven-plugin:4.8.6.2).
# Copies target/spotbugsXml.xml to evidencias/local/spotbugs/ and prints the
# number of <BugInstance> elements found.
# The scanner never fails the build: the quality gate decides, so this script
# exits 0 as long as the analysis ran.
#
# The named volume devsecops-maven-cache persists Maven dependencies so
# re-runs are fast.
set -Eeuo pipefail

REPORT_DIR="evidencias/local/spotbugs"
XML_SOURCE="target/spotbugsXml.xml"
XML_REPORT="${REPORT_DIR}/spotbugsXml.xml"

mkdir -p "${REPORT_DIR}"

echo "[SPOTBUGS] Running SpotBugs analysis in Docker..."

# 'clean compile' first: like the CI job, the classes must exist before the
# spotbugs goal runs (a direct goal invocation does not fork compilation).
if ! docker run --rm \
    -v "$PWD:/workspace" \
    -w /workspace \
    -v devsecops-maven-cache:/root/.m2/repository \
    maven:3.9-eclipse-temurin-21 \
    mvn -B clean compile com.github.spotbugs:spotbugs-maven-plugin:4.8.6.2:spotbugs; then
  echo "[SPOTBUGS] ERROR: SpotBugs Maven build failed, no report was produced." >&2
  exit 1
fi

if [[ ! -f "${XML_SOURCE}" ]]; then
  echo "[SPOTBUGS] ERROR: expected report not found: ${XML_SOURCE}" >&2
  exit 1
fi

cp "${XML_SOURCE}" "${XML_REPORT}"

# Count <BugInstance> occurrences. The XML is emitted on a single line, so
# 'grep -c' (matching lines) would always return 1; use 'grep -o | wc -l'.
BUG_COUNT="$(grep -o '<BugInstance' "${XML_REPORT}" | wc -l)"

echo "[SPOTBUGS] Report generated: ${XML_REPORT}"
echo "[SPOTBUGS] BugInstance count: ${BUG_COUNT}"
echo "[SPOTBUGS] Done (exit 0 on purpose: the quality gate decides, not the scanner)."
exit 0
