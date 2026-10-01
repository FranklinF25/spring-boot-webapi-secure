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
- [ ] T1 Setup: rama feature/devsecops-pipeline, Actions verificado, .gitignore evidencias/
- [ ] T2 Scripts locales Docker: scripts/local/{semgrep,dependency-check,spotbugs}.sh → reportes en evidencias/local/; verificar CVE-2022-42889 (commons-text 1.9) aparece en reporte DC
- [ ] T3 scripts/quality_gate.py: parsea semgrep JSON + dependency-check JSON + spotbugs XML; exit 1 si hallazgos CRITICAL; probar contra reportes reales de T2
- [ ] T4 security-semgrep.yml: fix comilla L5, checkout v4, subir artifact ya lo hace; gate lee su JSON
- [ ] T5 ci-sec.yml: Java 21, quality-gate descarga artifacts y ejecuta quality_gate.py (semgrep+spotbugs), sin SCA (vive en nightly)
- [ ] T6 ci-sec-nightly.yml: SCA activo, reporte JSON+HTML, caché NVD DB (actions/cache ~/.m2/repository/org/owasp/dependency-check-data), quitar `timezone:`, quitar `|| true`, gate lee los 3 reportes
- [ ] T7 ci-cd-sec.yml: triggers solo main/develop (quitar feature/**), Java 21, docker job también en develop, gate consistente
- [ ] T7b pom.xml: nvdApiKey → ${env.NVD_API_KEY}; crear dependency-check-suppressions.xml (vacío documentado); setear secret NVD_API_KEY en repo
- [ ] T8 Push + PR a main: checks corren; gate debe FALLAR si hay hallazgos críticos (esperado: falla por commons-text/semgrep errors) y pasar tras remediar o documentar decisión
- [ ] T9 Branch protection main: required status checks (nombres exactos de checks tras primera corrida), require PR, block merge si pipeline falla
- [ ] T10 Verificación final + evidencias organizadas en evidencias/ para capturas del PDF

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
