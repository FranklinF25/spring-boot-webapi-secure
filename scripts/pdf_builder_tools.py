#!/usr/bin/env python3
"""Build the local-tools TP evidence PDF (labs 01-07) from reports/ files
and screenshots in evidencias/capturas-tools/. Spanish content; tool logs
embedded verbatim. Runs in python:3.12-slim (build-pdf-tools.sh).
"""
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / "reports"
SHOTS = ROOT / "evidencias" / "capturas-tools"
OUT = ROOT / "evidencias" / "TP-DevSecOps-local-tools.pdf"

FONT = "Courier"


class PDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font(FONT, "I", 7)
            self.set_text_color(120)
            self.cell(0, 4, "TP DevSecOps - Herramientas locales (labs 01-07)", align="L")
            self.cell(0, 4, f"Página {self.page_no()}", align="R", new_x="LMARGIN", new_y="NEXT")
            self.ln(2)
            self.set_text_color(0)

    def title_page(self):
        self.set_font("Helvetica", "B", 19)
        self.ln(28)
        self.cell(0, 10, "Ejecución local de herramientas DevSecOps", new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("Helvetica", "B", 13)
        self.ln(2)
        self.cell(0, 8, "Labs 01-07 (guias-devsecops-local)", new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(8)
        self.set_font("Helvetica", "", 10)
        for line in (
            "Proyecto: spring-boot-webapi-secure (fork FranklinF25)",
            "Guías: github.com/pablovillazon/devsecops-ddsv1e3/guias-devsecops-local",
            "Todas las ejecuciones en Docker sobre el repositorio del proyecto",
            "Semgrep (SAST) | ZAP sobre Juice Shop (DAST) | Trivy (imágenes y SBOM)",
            "CycloneDX (SBOM) | Gitleaks (secretos) | Conftest (Policy as Code)",
            "Snyk (opcional): impedimento registrado, alternativa Lab 4 aplicada",
        ):
            self.cell(0, 6, line, new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(8)
        self.set_font("Helvetica", "I", 10)
        self.cell(0, 6, "Las capturas marcadas [PENDIENTE NN] aún no fueron provistas.", align="C", new_x="LMARGIN", new_y="NEXT")

    def h1(self, text):
        if self.get_y() > 240:
            self.add_page()
        self.ln(4)
        self.set_font("Helvetica", "B", 13)
        self.set_fill_color(230, 235, 240)
        self.cell(0, 9, text, new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(2)
        self.set_font("Helvetica", "", 10)

    def para(self, text, size=10):
        self.set_font("Helvetica", "", size)
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def mono(self, text, size=7.6):
        self.set_font(FONT, "", size)
        self.set_fill_color(245, 245, 245)
        for line in text.rstrip("\n").splitlines() or [""]:
            if self.get_y() > 275:
                self.add_page()
                self.set_font(FONT, "", size)
            self.cell(0, 4, line, new_x="LMARGIN", new_y="NEXT", fill=True)
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
            self.cell(0, 8, f"[PENDIENTE {num:02d}] {caption}  (falta: evidencias/capturas-tools/{name})", new_x="LMARGIN", new_y="NEXT")
            self.set_text_color(0)
        self.ln(1)

    def read(self, rel, limit=60):
        p = REPORTS / rel
        if not p.exists():
            return f"(archivo inexistente: reports/{rel})"
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

    # Lab 1
    pdf.add_page()
    pdf.h1("Lab 1 - SAST con Semgrep (p/java)")
    pdf.mono(
        "$ docker run --rm -v \"${PWD}:/src\" -w /src semgrep/semgrep:latest \\\n"
        "    semgrep scan --config p/java --json --output /src/reports/semgrep-report.json src/main/java\n"
        "\n"
        "Resultado código actual (post-remediación TP anterior): 0 hallazgos, 0 errores.\n"
        "Mismo comando sobre fuentes originales (584fd8d): 3 hallazgos:\n"
        "  ERROR tainted-html-string  CommentController.java:19 (XSS reflejado)\n"
        "  ERROR tainted-sql-string   ProductController.java:24 (SQLi)\n"
        "  WARN  spring-sqli          ProductController.java:25\n"
        "Cobertura demostrada: el 0 actual es efecto de la remediación verificada."
    )
    pdf.para("Detalle en reports/lab1-resumen.md. Contexto guardado en semgrep-original-contexto.json.")
    pdf.shot(1, "01-lab1-semgrep.png", "Terminal: escaneo Semgrep p/java en Docker")

    # Lab 2
    pdf.add_page()
    pdf.h1("Lab 2 - DAST baseline ZAP sobre Juice Shop")
    pdf.mono(
        "$ docker network create devsecops-lab\n"
        "$ docker run --rm -d --name juice-shop --network devsecops-lab -p 127.0.0.1:3000:3000 bkimminich/juice-shop\n"
        "$ docker run --rm --network devsecops-lab --user root -v \"${PWD}/reports:/zap/wrk:rw\" \\\n"
        "    ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://juice-shop:3000 -m 1 -T 5 \\\n"
        "    -r zap-report.html -J zap-report.json\n"
        "\n"
        "Exit: 2 (WARN sin FAIL, como prevé la guía)\n"
        "FAIL-NEW: 0  WARN-NEW: 8  INFO: 0  PASS: 59\n"
        "Alertas WARN: CSP no configurada (Medium), Cross-Domain Misconfig (Medium),\n"
        "COOP/COEP ausentes, Dangerous JS Functions (eval en main.js), Feature-Policy\n"
        "deprecado, Timestamp Disclosure. Baseline pasivo: no ejercita lógica de negocio."
    )
    pdf.para("Tres alertas con evidencia y mitigación en reports/lab2-resumen.md; teardown de red y contenedor ejecutado.")
    pdf.shot(2, "02-lab2-juice.png", "Juice Shop respondiendo en 127.0.0.1:3000")
    pdf.shot(3, "03-lab2-zap.png", "Terminal: ejecución de zap-baseline.py y resumen final")
    pdf.shot(4, "04-lab2-zap-html.png", "Reporte HTML de ZAP (zap-report.html) en el navegador")

    # Lab 3
    pdf.add_page()
    pdf.h1("Lab 3 - Vulnerabilidades de imágenes con Trivy")
    pdf.mono(
        "nginx:1.24.0 (debian 11.9, digest sha256:6c0218f168766...):\n"
        "  Total: 731 (CRITICAL: 17, HIGH: 174, MEDIUM: 287, LOW: 237)\n"
        "  Gate HIGH,CRITICAL --exit-code 1 -> exit 1: \"Total: 191 (HIGH: 174, CRITICAL: 17)\"\n"
        "nginx:stable (debian 13, digest sha256:3a8edbda21b63...):\n"
        "  Total: 313 (CRITICAL: 1 sin fix CVE-2026-6653 libxml2, HIGH: 66)\n"
        "CVEs seleccionados (before -> after):\n"
        "  CVE-2024-45491 libexpat1 CRITICAL 2.2.10-2+deb11u5 -> fix 2.2.10-2+deb11u6: DESAPARECIÓ en stable\n"
        "  CVE-2024-45492 libexpat1 CRITICAL (ídem): DESAPARECIÓ en stable"
    )
    pdf.para("Cambio propuesto: migrar a estable por digest; stable no está limpia (1 CRITICAL sin fix) - detalle en reports/lab3-resumen.md.")
    pdf.shot(5, "05-lab3-trivy-gate.png", "Terminal: gate Trivy exit 1 sobre nginx:1.24.0")
    pdf.shot(6, "06-lab3-trivy-stable.png", "Terminal: escaneo de nginx:stable")

    # Lab 4
    pdf.add_page()
    pdf.h1("Lab 4 - SBOM CycloneDX + SCA Trivy")
    pdf.mono(
        "$ mvn -B dependency:tree | mvn -B clean verify (4/4 tests) | makeAggregateBom (CycloneDX 2.9.3)\n"
        "$ trivy sbom --scanners vuln --format json --output sca-before.json target/bom.json\n"
        "\n"
        "BEFORE: 2 hallazgos\n"
        "  MEDIUM  CVE-2026-49844  log4j-api 2.24.3 -> fix 2.25.5/2.26.1\n"
        "  CRITICAL CVE-2026-47884  spring-webmvc 6.2.19 -> fix solo en 7.0.9 (línea Boot 4)\n"
        "REMEDIACIÓN: <log4j2.version>2.26.1</log4j2.version> + mvn clean verify 4/4 tests\n"
        "AFTER: 1 hallazgo (solo spring-webmvc; log4j desapareció)\n"
        "SBOMs conservados: lab4-bom-BEFORE.json / lab4-bom-AFTER.json"
    )
    pdf.para("Pendiente documentado: CVE-2026-47884 requiere migración de plataforma (Spring Boot 4), no es patch de la línea 3.5.x. Detalle en reports/lab4-resumen.md.")
    pdf.shot(7, "07-lab4-sbom.png", "Terminal: generación del SBOM y escaneo trivy sbom")
    pdf.shot(8, "08-lab4-after.png", "Terminal: sca-after.json con el hallazgo log4j eliminado")

    # Lab 5
    pdf.add_page()
    pdf.h1("Lab 5 - Detección de secretos con Gitleaks")
    pdf.mono(
        "Regla didáctica demo-token (DEMO_TOKEN_[A-Z0-9]{16}) + valor ficticio en secret-demo/demo.env.\n"
        "dir secret-demo (antes):     1 leak  -> gitleaks-before.json (secreto REDACTADO, exit 1)\n"
        "reemplazo por REPLACE_AT_RUNTIME\n"
        "dir secret-demo (después):   0 leaks -> gitleaks-after.json (exit 0)\n"
        "git /repo (historial, reglas default): 0 leaks -> gitleaks-history.json\n"
        "\n"
        "Observación: la NVD API key del historial upstream (hallada manualmente en el TP\n"
        "anterior) NO es detectada por patrones default (UUID sin prefijo de proveedor):\n"
        "la detección por patrones complementa, no reemplaza, revisión y push protection."
    )
    pdf.para("Archivos de demostración retirados al cierre (paso 8 de la guía). Detalle en reports/lab5-resumen.md.")
    pdf.shot(9, "09-lab5-gitleaks.png", "Terminal: escaneo gitleaks con 1 leak detectado (antes)")

    # Lab 6
    pdf.add_page()
    pdf.h1("Lab 6 - Policy as Code con Conftest")
    pdf.mono(
        "policy/compose.rego (Rego v1): deny si service.privileged == true\n"
        "compose-lab.yaml privileged: true  -> FAIL \"Servicio app: privileged=true no permitido\"\n"
        "                                     1 test, 0 passed, 1 failure (exit 1)\n"
        "compose-lab.yaml privileged: false -> PASS 1 test, 1 passed, 0 failures (exit 0)\n"
        "Reportes: conftest-before.json / conftest-after.json"
    )
    pdf.para("La política prueba solo privileged; pasar la regla no garantiza configuración segura. Detalle en reports/lab6-resumen.md.")
    pdf.shot(10, "10-lab6-conftest.png", "Terminal: conftest FAIL con privileged:true y PASS con false")

    # Lab 7
    pdf.h1("Lab 7 - SCA con Snyk (opcional): impedimento registrado")
    pdf.para(
        "Snyk exige cuenta y autenticación interactiva (navegador), no disponible en este entorno "
        "automatizado. Según la propia guía, se registra el impedimento y se aplica el Lab 4 como "
        "alternativa (SCA de Maven con remediación verificada). Pasos para completarlo con cuenta "
        "propia en reports/lab7-resumen.md."
    )

    # Entregables
    pdf.h1("Entregables generados (reports/)")
    pdf.mono(
        "lab1: semgrep-report.json, semgrep-original-contexto.json, lab1-resumen.md\n"
        "lab2: zap-report.html, zap-report.json, lab2-resumen.md\n"
        "lab3: trivy-before.json, trivy-gate.txt, trivy-after.json, lab3-resumen.md\n"
        "lab4: lab4-dependency-tree.txt, lab4-bom-BEFORE/AFTER.json, sca-before/after.json, lab4-resumen.md\n"
        "lab5: gitleaks-before/after/history.json, lab5-resumen.md\n"
        "lab6: compose-lab.yaml, policy/compose.rego, conftest-before/after.json, lab6-resumen.md\n"
        "lab7: lab7-resumen.md (impedimento)"
    )

    pdf.output(str(OUT))
    print(f"written: {OUT}")


if __name__ == "__main__":
    main()
