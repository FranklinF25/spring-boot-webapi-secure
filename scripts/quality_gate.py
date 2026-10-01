#!/usr/bin/env python3
"""Security quality gate for the DevSecOps lab.

Reads scanner reports produced by scripts/local/*.sh and fails when critical
findings are present. The gate never passes on a missing or unparseable
report.

Usage:
    python3 scripts/quality_gate.py [--semgrep FILE.json]
                                    [--dependency-check FILE.json]
                                    [--spotbugs FILE.xml]

Critical criteria:
    Semgrep           extra.severity == "ERROR"
    Dependency-Check  severity == "critical" (case-insensitive) or
                      cvssv3 base score >= 9.0
    SpotBugs          BugInstance priority == 1 (High), or rank <= 4 when
                      the priority attribute is absent

Exit codes:
    0  QUALITY GATE PASSED (no critical findings)
    1  QUALITY GATE FAILED (N critical findings)
    2  usage error, or a requested report is missing/unparseable
"""

import argparse
import json
import sys
import xml.etree.ElementTree as ET

GATE_TAG = "[GATE]"
MAX_LISTED_FINDINGS = 10


def fail_gate(message):
    """Abort with exit code 2: the gate never passes on bad input."""
    print(f"{GATE_TAG} ERROR: {message}", file=sys.stderr)
    sys.exit(2)


def load_json(path, tool_label):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except OSError as exc:
        fail_gate(f"cannot read {tool_label} report '{path}': {exc}")
    except json.JSONDecodeError as exc:
        fail_gate(f"invalid JSON in {tool_label} report '{path}': {exc}")


def cvssv3_base_score(vulnerability):
    """Return the CVSSv3 base score as float, or None when unavailable."""
    cvssv3 = vulnerability.get("cvssv3")
    if not isinstance(cvssv3, dict):
        return None
    for key in ("baseScore", "base-score", "base_score"):
        value = cvssv3.get(key)
        if value is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                return None
    return None


def parse_semgrep(path):
    """Yield critical findings from a Semgrep JSON report."""
    data = load_json(path, "Semgrep")
    criticals = []
    for result in data.get("results", []):
        severity = (result.get("extra") or {}).get("severity", "")
        if severity != "ERROR":
            continue
        rule = result.get("check_id") or result.get("rule_id") or "unknown-rule"
        line = (result.get("start") or {}).get("line", "?")
        criticals.append(
            {
                "id": rule,
                "severity": severity,
                "location": f'{result.get("path", "?")}:{line}',
            }
        )
    return criticals


def parse_dependency_check(path):
    """Yield critical findings from an OWASP Dependency-Check JSON report."""
    data = load_json(path, "dependency-check")
    criticals = []
    for dependency in data.get("dependencies", []):
        for vulnerability in dependency.get("vulnerabilities") or []:
            severity = str(vulnerability.get("severity") or "").lower()
            score = cvssv3_base_score(vulnerability)
            if severity != "critical" and not (score is not None and score >= 9.0):
                continue
            cve = vulnerability.get("name") or "unknown-CVE"
            artifact = dependency.get("fileName")
            criticals.append(
                {
                    "id": cve,
                    "severity": severity or f"cvss {score}",
                    "location": f"{cve} in {artifact}" if artifact else cve,
                }
            )
    return criticals


def local_name(tag):
    """Strip the XML namespace, if any, from an element tag."""
    return tag.rsplit("}", 1)[-1]


def parse_spotbugs(path):
    """Yield high-priority findings from a SpotBugs XML report."""
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as exc:
        fail_gate(f"cannot parse SpotBugs XML report '{path}': {exc}")
    criticals = []
    for instance in root.iter():
        if local_name(instance.tag) != "BugInstance":
            continue
        priority = instance.get("priority")
        if priority is not None:
            is_high = priority == "1"
        else:
            try:
                is_high = int(instance.get("rank", "99")) <= 4
            except ValueError:
                is_high = False
        if not is_high:
            continue
        source = next(
            (
                element
                for element in instance.iter()
                if local_name(element.tag) == "SourceLine" and element.get("classname")
            ),
            None,
        )
        if source is None:
            location = "unknown source"
        else:
            location = source.get("classname", "?")
            if source.get("start"):
                location += f':{source.get("start")}'
        criticals.append(
            {
                "id": instance.get("type", "unknown-bug"),
                "severity": "priority 1 (High)",
                "location": location,
            }
        )
    return criticals


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Security quality gate: fails on critical findings in scanner reports."
    )
    parser.add_argument("--semgrep", metavar="FILE.json", help="Semgrep JSON report")
    parser.add_argument(
        "--dependency-check", metavar="FILE.json", help="OWASP Dependency-Check JSON report"
    )
    parser.add_argument("--spotbugs", metavar="FILE.xml", help="SpotBugs XML report")
    args = parser.parse_args(argv)

    sources = [
        ("SEMGREP", args.semgrep, parse_semgrep),
        ("DEPENDENCY-CHECK", args.dependency_check, parse_dependency_check),
        ("SPOTBUGS", args.spotbugs, parse_spotbugs),
    ]
    if not any(path for _, path, _ in sources):
        parser.print_usage(sys.stderr)
        fail_gate("no reports provided; pass at least one of the report flags")

    findings = []
    for tool_label, path, parse in sources:
        if not path:
            continue
        criticals = parse(path)
        print(f"[{tool_label}] {len(criticals)} critical finding(s)")
        findings.extend((tool_label, finding) for finding in criticals)

    if not findings:
        print(f"{GATE_TAG} QUALITY GATE PASSED")
        return 0

    print(f"{GATE_TAG} critical findings (listing up to {MAX_LISTED_FINDINGS}):")
    for index, (tool_label, finding) in enumerate(findings[:MAX_LISTED_FINDINGS], start=1):
        print(
            f"{GATE_TAG}   {index}. [{tool_label}] "
            f"{finding['id']} | {finding['severity']} | {finding['location']}"
        )
    hidden = len(findings) - MAX_LISTED_FINDINGS
    if hidden > 0:
        print(f"{GATE_TAG}   ... and {hidden} more")
    print(f"{GATE_TAG} QUALITY GATE FAILED: {len(findings)} critical findings")
    return 1


if __name__ == "__main__":
    sys.exit(main())
