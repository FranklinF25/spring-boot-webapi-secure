# Feature: Labs locales DevSecOps (guias-devsecops-local)

## Objective
Ejecutar las guías 01-07 de pablovillazon/devsecops-ddsv1e3/guias-devsecops-local sobre este repo, todo en Docker, generando reports/ + resúmenes por lab, y armar el PDF de evidencias TP-DevSecOps-local-tools.pdf.

## Problem / Why
Nueva tarea del TP: ejecución local de herramientas (Semgrep SAST, ZAP DAST sobre Juice Shop, Trivy imágenes, SBOM+SCA, Gitleaks, Conftest, Snyk opcional) con entregable PDF con capturas.

## Constraints
- Todo en Docker (misma restricción del usuario que la tarea anterior).
- Seguir los comandos de las guías lo más literalmente posible; maven vía contenedor maven:3.9-eclipse-temurin-21 con volumen devsecops-maven-cache.
- Lab 7 Snyk requiere auth interactiva → documentar impedimento salvo que el usuario tenga cuenta.
- reports/ gitignored; demo files del lab 5 se retiran al final (guía paso 8); lab6 entrega compose-lab.yaml + policy/compose.rego (se conservan).

## Route per task
- Ejecución de labs: inline (comandos prescriptivos de guías, evidencia debe quedar en reports/).
- PDF + capturas: mismo patrón que TP anterior (builder + placeholders + capturas del usuario).

## Tasks
- [x] Setup (feature doc, gitignore, pulls)
- [x] Lab 1 Semgrep p/java (scan → hallazgos → fix rama lab → mvn test → re-scan → lab1-resumen.md)
- [x] Lab 3 Trivy imágenes (nginx:1.24.0 before + gate + nginx:stable after + lab3-resumen.md)
- [x] Lab 4 SBOM+SCA (dependency:tree, verify, cyclonedx bom.json, trivy sbom before, update dep/parent si aplica, after, lab4-resumen.md)
- [x] Lab 5 Gitleaks (regla demo + demo.env before/after + history scan + lab5-resumen.md + limpieza)
- [x] Lab 6 Conftest (compose privileged true→false + rego + before/after + lab6-resumen.md)
- [x] Lab 2 ZAP+Juice Shop (network + baseline HTML/JSON + lab2-resumen.md + teardown)
- [x] Lab 7 Snyk: impedimento documentado o cuenta del usuario
- [x] PDF evidencias + lista capturas

## Acceptance criteria
- reports/ con todos los entregables de cada guía (JSONs + resúmenes .md).
- Cada lab ejecutado con los comandos de la guía en Docker; salidas verificadas (no inventadas).
- PDF generado con evidencia textual + placeholders de capturas para el usuario.

## Checks
- Salidas de comandos verificadas por lab (exit codes esperados según cada guía).
- JSONs de reporte parseables y no vacíos (salvo alcance documentado).

## Progress log
- [2026-10-06] Setup: pulls background (juice-shop, zap, gitleaks, conftest), reports/ gitignored.

## Notes
- Lab 4: repo ya remediado (parent 3.5.16, tomcat 10.1.60, jackson 2.21.7). Trivy sbom verá CVEs de spring sin fix en línea (DC suppressions no aplican a Trivy). Buscar update real posible (log4j-api 2.24.3 con CVE-2026-49844: verificar si existe 2.24.4+/override log4j2.version).
- Lab 5 history scan va a detectar la NVD key del upstream en el historial → hallazgo REAL a documentar (rotación recomendada, es del profe).
- Lab 2: baseline puede tardar 2-5 min; exit code 2 (WARN) esperable.

## Cierre [2026-10-06]
- Labs 1-7 ejecutados en Docker, reportes en reports/ (gitignored), resumenes por lab.
- Lab 4 aplico remediacion real: log4j2.version 2.26.1 (pendiente commitear el pom a un PR).
- PDF: evidencias/TP-DevSecOps-local-tools.pdf (7 paginas, espanol, [PENDIENTE 01-10] para capturas del usuario).
- Lista de capturas: evidencias/capturas-tools/README.md.
