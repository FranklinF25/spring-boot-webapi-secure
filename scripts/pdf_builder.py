#!/usr/bin/env python3
"""Build the TP evidence PDF from local evidence files and screenshots.

Runs inside python:3.12-slim (see scripts/local/build-pdf.sh). Content in
Spanish (user request); execution logs are embedded verbatim. A4, embedded
monospace evidence blocks and numbered screenshots.
"""
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parent.parent
EVID = ROOT / "evidencias"
SHOTS = EVID / "capturas"
OUT = EVID / "TP-DevSecOps-evidencias.pdf"

REPO = "FranklinF25/spring-boot-webapi-secure"
BASE = f"https://github.com/{REPO}"

FONT = "Courier"
MONO_H = 8


class PDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font(FONT, "I", 7)
            self.set_text_color(120)
            self.cell(0, 4, "TP DevSecOps - spring-boot-webapi-secure", align="L")
            self.cell(0, 4, f"Página {self.page_no()}", align="R", new_x="LMARGIN", new_y="NEXT")
            self.ln(2)
            self.set_text_color(0)

    def title_page(self):
        self.set_font("Helvetica", "B", 20)
        self.ln(30)
        self.cell(0, 10, "Pipeline DevSecOps - Reporte de Evidencias", new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("Helvetica", "", 12)
        self.ln(4)
        self.cell(0, 8, "spring-boot-webapi-secure (fork)", new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(6)
        self.set_font("Helvetica", "", 10)
        for line in (
            f"Repositorio: {BASE}",
            "Análisis locales: Semgrep, OWASP Dependency-Check y SpotBugs (todos en Docker)",
            "Pipelines: CI [feature/**] | CI/CD [main, develop] | Nightly + SCA",
            "El quality gate lee los reportes (Semgrep/Dependency-Check/SpotBugs) y falla ante hallazgos CRITICAL",
            "main protegida: merges bloqueados si los checks requeridos fallan",
        ):
            self.cell(0, 6, line, new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(10)
        self.set_font("Helvetica", "I", 10)
        self.cell(0, 6, "Las capturas marcadas [PENDIENTE NN] aún no fueron provistas.", align="C", new_x="LMARGIN", new_y="NEXT")

    def h1(self, text):
        if self.get_y() > 240:
            self.add_page()
        self.ln(4)
        self.set_font("Helvetica", "B", 14)
        self.set_fill_color(230, 235, 240)
        self.cell(0, 9, text, new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(2)
        self.set_font("Helvetica", "", 10)

    def para(self, text, size=10):
        self.set_font("Helvetica", "", size)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def mono(self, text, size=MONO_H):
        self.set_font(FONT, "", size)
        self.set_fill_color(245, 245, 245)
        self.set_draw_color(200)
        for line in text.rstrip("\n").splitlines() or [""]:
            if self.get_y() > 275:
                self.add_page()
                self.set_font(FONT, "", size)
            self.cell(0, 4.2, line, new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(2)
        self.set_text_color(0)

    def shot(self, num, name, caption):
        path = SHOTS / name
        if self.get_y() > 200:
            self.add_page()
        self.set_font("Helvetica", "B", 10)
        if path.exists():
            self.cell(0, 6, f"[Captura {num:02d}] {caption}", new_x="LMARGIN", new_y="NEXT")
            self.image(str(path), w=min(180, self.epw))
            self.ln(2)
        else:
            self.set_text_color(180, 60, 60)
            self.cell(0, 8, f"[PENDIENTE {num:02d}] {caption}  (falta: evidencias/capturas/{name})", new_x="LMARGIN", new_y="NEXT")
            self.set_text_color(0)
        self.ln(1)

    def read(self, rel, limit=80):
        p = EVID / rel
        if not p.exists():
            return f"(archivo de evidencia inexistente: {rel})"
        lines = p.read_text(errors="replace").splitlines()
        body = "\n".join(lines[:limit])
        if len(lines) > limit:
            body += f"\n... ({len(lines) - limit} líneas más)"
        return body or "(vacío)"


def main():
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.title_page()

    # 1. Resumen
    pdf.add_page()
    pdf.h1("1. Resumen: gate rojo -> merge bloqueado -> remediación -> verde")
    pdf.para(
        "La aplicación de laboratorio incluye hallazgos críticos deliberados. El quality gate lee los "
        "reportes de los escáneres (Semgrep JSON, Dependency-Check JSON, SpotBugs XML), falla ante hallazgos "
        "críticos, y la protección de rama en main bloquea el merge mientras un check requerido este en rojo. "
        "Los hallazgos se remediaron (correcciónes de código + actualización de dependencias + supresiones "
        "documentadas) y el mismo PR pasó de BLOCKED a CLEAN y se fusiónó."
    )
    pdf.mono(
        "Antes de la remediación (gate local, código original):\n"
        "  [SEMGREP]            7 críticos  (SQLi, XSS, secretos hardcodeados, permitAll)\n"
        "  [DEPENDENCY-CHECK]  28 críticos  (CVE-2022-42889 commons-text 1.9 + CVEs de plataforma)\n"
        "  [SPOTBUGS]           0 críticos\n"
        "  QUALITY GATE FAILED: 35 critical findings   (exit 1)\n"
        "\n"
        "Después de la remediación (gate local, código final):\n"
        + pdf.read("local/gate-DESPUES-final.txt", limit=10)
    )

    # 2. Pipelines
    pdf.add_page()
    pdf.h1("2. Ejecuciones del pipeline (GitHub Actions)")
    pdf.para("Corridas referenciadas; las capturas siguen a continuacion. Los logs literales se muestran en ingles (salida real de las herramientas).")
    pdf.mono(
        "ROJO   CI gate fallando por críticos  : " + BASE + "/actions/runs/36891803279\n"
        "VERDE  CI en PR #1 (tras los fixes)   : " + BASE + "/actions/runs/36904456901\n"
        "VERDE  CI/CD en main (docker + GHCR)  : " + BASE + "/actions/runs/37024004945\n"
        "VERDE  Nightly + SCA                  : " + BASE + "/actions/runs/37024843981\n"
        "Regla de protección de main           : " + BASE + "/settings/branches\n"
        "PR #1 (bloqueado -> limpio -> fusión) : " + BASE + "/pull/1"
    )
    pdf.shot(1, "01-gate-rojo-ci.png", "Job Quality Gate en rojo: 7 hallazgos críticos listados (corrida 36891803279)")
    pdf.shot(2, "02-pr1-checks-historial.png", "PR #1: historial de checks (corridas fallidas y luego verdes)")
    pdf.shot(3, "03-protección-main.png", "Protección de rama: checks requeridos Build & Test + Quality Gate")
    pdf.shot(4, "04-ci-verde-pr.png", "CI en verde en el PR #1 tras la remediación")
    pdf.shot(5, "05-cicd-main-verde.png", "CI/CD en verde en main, incluye Docker Build -> Scan -> Push")
    pdf.shot(6, "06-ghcr-imagen.png", "Imagen de contenedor publicada en GHCR")
    pdf.shot(7, "07-nightly-verde.png", "Nightly en verde con el job SCA - OWASP Dependency-Check")
    pdf.shot(8, "08-nightly-artifact.png", "Artifact dependency-check-report del nightly")

    # 3. Logs del gate
    pdf.add_page()
    pdf.h1("3. Salida del quality gate (logs reales)")
    pdf.para("3.1 Gate fallando en CI antes de la remediación (extraido del log del job, corrida 36891803279):")
    pdf.mono(pdf.read("local/gate-ANTES-ci-log.txt", limit=16))
    pdf.para("3.2 Gate fallando localmente sobre el código ORIGINAL vulnerable (Semgrep en Docker sobre las fuentes previas al fix, reproduciendo el estado inicial):")
    pdf.mono(pdf.read("local/gate-ANTES-local-original.txt", limit=12))
    pdf.para("3.3 Gate pasando localmente tras la remediación (reportes generados en Docker):")
    pdf.mono(pdf.read("local/gate-DESPUES-final.txt", limit=10))

    # 4. Análisis locales
    pdf.add_page()
    pdf.h1("4. Análisis locales en Docker")
    pdf.para(
        "Todos los escaneos locales corren en contenedores (semgrep/semgrep, maven:3.9-eclipse-temurin-21 con "
        "los plugins Maven de dependency-check y spotbugs). Los reportes se guardan en evidencias/local/."
    )
    pdf.mono(
        "scripts/local/semgrep.sh            -> evidencias/local/semgrep/semgrep-results.json (+SARIF)\n"
        "scripts/local/dependency-check.sh   -> evidencias/local/dependency-check/dependency-check-report.html/.json\n"
        "scripts/local/spotbugs.sh           -> evidencias/local/spotbugs/spotbugsXml.xml\n"
        "scripts/local/gate.sh               -> ejecuta quality_gate.py sobre los 3 reportes"
    )
    pdf.shot(9, "09-local-semgrep.png", "Terminal: escaneo de Semgrep en Docker")
    pdf.shot(10, "10-local-dc-terminal.png", "Terminal: OWASP Dependency-Check en Docker")
    pdf.shot(11, "11-local-dc-html.png", "Reporte HTML de Dependency-Check (navegador)")
    pdf.shot(12, "12-local-spotbugs.png", "Terminal: SpotBugs en Docker")
    pdf.shot(13, "13-gate-local-verde.png", "Quality gate local PASSED (tres reportes)")

    # 5. Tabla comparativa
    pdf.add_page()
    pdf.h1("5. Comparación antes / después")
    rows = [
        ("Métrica", "Antes", "Después"),
        ("Hallazgos ERROR de Semgrep", "7", "0 (quedan 2 WARNING)"),
        ("Críticos de Dependency-Check", "28", "0 (7 CVEs suprimidos, documentados)"),
        ("Críticos de SpotBugs (prio 1)", "0", "0 (2 medios)"),
        ("Quality gate", "FAILED (exit 1)", "PASSED (exit 0)"),
        ("Merge a main", "BLOCKED", "CLEAN (PR #1 fusiónado)"),
        ("Parent de Spring Boot", "3.5.14", "3.5.16"),
        ("tomcat-embed-core", "10.1.55", "10.1.60"),
        ("jackson-databind", "2.21.4", "2.21.7"),
        ("commons-text", "1.9 (CVE-2022-42889)", "eliminada (dependencia solo del lab)"),
    ]
    pdf.set_font("Helvetica", "B", 9)
    for col, w in zip(rows[0], (70, 55, 55)):
        pdf.cell(w, 7, col, border=1)
    pdf.ln()
    pdf.set_font("Helvetica", "", 9)
    for row in rows[1:]:
        for val, w in zip(row, (70, 55, 55)):
            pdf.cell(w, 6.5, val, border=1)
        pdf.ln()
    pdf.ln(3)
    pdf.para(
        "Correcciones de código: inyección SQL -> query parametrizada (ProductController); XSS reflejado -> "
        "HtmlUtils.htmlEscape (CommentController); credenciales hardcodeadas -> propiedades @Value con "
        "override por variables de entorno (AuthController); permitAll global -> authenticated con los "
        "endpoints públicos login/preview/health (SecurityConfig)."
    )

    # 6. Riesgos aceptados
    pdf.h1("6. Pendientes y riesgo aceptado (documentado)")
    pdf.mono(
        "- 7 CVEs en spring-core/web 6.2.19 y spring-security 6.5.11: no existe versión corregida dentro de\n"
        "  las líneas gestionadas por Spring Boot 3.5.16 (última estable). Aceptados para este lab aislado\n"
        "  (solo localhost) en dependency-check-suppressions.xml con nota de revision.\n"
        "- WARNINGs de Semgrep que se mantienen: csrf deshabilitado (lab) y sensitive-data-in-log (quirk de la regla).\n"
        "- Un '// nosemgrep' acotado sobre tainted-html-string (la regla del registry no modela sanitizadores;\n"
        "  el escape está verificado por tests).\n"
        "- Un 429 transitorio de Maven Central hizo fallar una corrida del nightly; se resolvio con re-run\n"
        "  de los jobs fallidos.\n"
        "- La NVD API key del repositorio original sigue en el historial publico upstream; se recomienda rotarla."
    )

    pdf.shot(14, "14-resultado-bloqueo-gh.png", "(opcional) gh CLI mostrando el estado BLOCKED del merge")
    pdf.shot(15, "15-security-tab.png", "(opcional) pestaña Security: alertas de code scanning")

    pdf.output(str(OUT))
    print(f"written: {OUT}")


if __name__ == "__main__":
    main()
