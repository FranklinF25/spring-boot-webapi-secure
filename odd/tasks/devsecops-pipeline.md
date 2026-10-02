# Feature: Endurecimiento del pipeline DevSecOps (TP)

## Objective
Dejar el fork `FranklinF25/spring-boot-webapi-secure` funcional con: análisis locales en Docker (Semgrep, OWASP Dependency Check, SpotBugs), workflows CI [feature/**], CI/CD [main, develop], nightly + SCA, quality gate que LEE reportes y falla ante hallazgos CRITICAL, y merges a main bloqueados si el pipeline falla.

## Problem / Why
TP de DevSecOps. El repo base trae 4 workflows con defectos: SCA deshabilitado (`if: false`) en ci-sec/ci-cd-sec por lo lento de la sincronización NVD, gates anulados con `|| true`, quality gate que solo mira `needs.*.result` y no parsea reportes, API key NVD filtrada en pom.xml L94, Java 25 (workflows) vs 21 (pom), trigger push roto en security-semgrep.yml L5 (comilla), `dependency-check-suppressions.xml` referenciado e inexistente, `timezone:` no soportado en schedule del nightly, solapamiento de triggers feature/** entre ci-sec y ci-cd-sec.

## Constraints (user)
- TODO en Docker para ejecuciones locales de herramientas (Semgrep, Dependency Check, SpotBugs, Maven).
- Paso lento de CI (NVD sync de Dependency Check) debe mitigarse: API key como secret + caché de la base NVD en Actions.
- Entregable final: PDF con capturas (responsabilidad del usuario; el pipeline debe dejar evidencias descargables/artifacts).

## Scope (authorized)
- Repo local /home/uni/dev/dimo5/spring-boot-webapi-secure, branch feature/devsecops-pipeline.
- Workflows, pom.xml (migración de key), scripts/ locales en Docker, scripts/quality_gate.py, branch protection vía gh api, carpeta evidencias/ (gitignored, uso local).

## Route per task
- T2 local scripts: delegated writer (multi-file) + verificación inline con docker run.
- T3 quality gate script: delegated writer junto con T2, verificación inline contra reportes reales.
- T4-T7 workflows: delegated writer (4 archivos YAML interdependientes) + actionlint inline.
- T8-T9 push/PR/protection: inline (estado git/gh).

## Tasks
- [x] T1 Setup: rama feature/devsecops-pipeline, Actions verificado, .gitignore evidencias/
- [x] T2 Scripts locales Docker: semgrep.sh / dependency-check.sh / spotbugs.sh → reportes en evidencias/local/ (commits 3155db2, 84fb66d)
- [x] T3 scripts/quality_gate.py: probado contra reportes REALES → exit 1 con 35 críticos (7 semgrep + 28 DC + 0 spotbugs), exit 2 faltante, exit 0 limpio
- [x] T4 security-semgrep.yml: fix quoting, solo workflow_dispatch (commit 582337a)
- [x] T5 ci-sec.yml: Java 21, sast-semgrep, gate descarga artifacts y corre quality_gate.py
- [x] T6 ci-sec-nightly.yml: SCA activo, caché NVD rodante, sin timezone, gate lee 3 reportes
- [x] T7 ci-cd-sec.yml: solo main/develop, docker job en develop, DEPLOY_ENABLED switch
- [x] T7b pom: key NVD eliminada (secret NVD_API_KEY seteado en repo), suppressions creado; plugin 12.1.3 + formats pom + ossindex off (84fb66d)
- [x] T8a Push + PR #1 + checks verificados: 4 scanners success, Quality Gate failure leyendo reportes (7 semgrep criticals en log) — corridas 36891803279/8230
- [x] T8b Remediación (commit 449cdd1): 7 fixes de código + parent 3.5.16 + tomcat 10.1.60 + suppressions documentadas (7 CVEs sin fix en línea gestionada) → gate exit 0 local; CI verde (36904456901/755); PR state CLEAN → mergeado a main
- [x] T9 Branch protection main (antes de remediar): required checks estrictos 'Build & Test' + 'Quality Gate', sin force-push; evidencia BLOCKED capturada pre-fix y CLEAN post-fix
- [x] T10a Bugfixes latentes del CI/CD en main (PRs #2-#7): tag trivy-action v-prefijado, maven wrapper faltante, usuario alpine, healthcheck wget, actuator/health permitAll, jackson 2.21.7 (3 HIGH Trivy imagen), GHCR minúsculas, image-ref único, trivy dos pasadas (gate tabla + SARIF). CI/CD main SUCCESS (37024004945)
- [x] T10b Nightly + SCA en CI: SUCCESS (37021958375) con gate leyendo los 3 reportes; re-dispatch final sobre main definitivo
- [x] T10c Evidencias para PDF organizadas en evidencias/README.md (URLs de corridas roja/verde, tabla comparativa antes/después, pendientes conocidos)

## Acceptance criteria — VERIFICADOS
- ✅ Los 3 workflows + semgrep manual corren verdes; nightly con SCA y caché NVD rodante.
- ✅ quality_gate.py exit 1 ante CRITICAL (35 reales: 7 semgrep + 28 DC incl. CVE-2022-42889) y exit 0 tras remediación; demostrado local y en CI (corrida roja 36891803279).
- ✅ main protegida: PR #1 BLOCKED con gate rojo → CLEAN tras remediar → mergeado.
- ✅ Reportes locales en Docker generados en evidencias/local/ (semgrep, DC, spotbugs).

## Acceptance criteria
- Los 3 workflows + semgrep corren en el fork sin errores de sintaxis; nightly con SCA y caché NVD.
- quality_gate.py exit≠0 ante CRITICAL (demostrado con reportes reales que contienen commons-text).
- main protegida: merge bloqueado sin checks verdes.
- Hallazgos locales en Docker generados y guardados en evidencias/ para el PDF.

## Checks
- actionlint (docker: rhysd/actionlint) sobre los 4 YAML
- mvn verify (docker: maven:3.9-eclipse-temurin-21)
- quality_gate.py contra reportes reales (caso crítico y caso limpio)
- gh api checks del PR

## Progress log
- [2026-10-01] T1 en curso: rama creada, Actions del fork verificado (enabled=all).

## Notes
- NVD key filtrada es del profe (repo público upstream); se migra a secret con el mismo valor por practicidad y se documenta que puede reemplazarse.
- TDD mode: off (trabajo de infra/YAML; verificación funcional con actionlint + ejecución real de herramientas + script gate probado contra reportes reales).
