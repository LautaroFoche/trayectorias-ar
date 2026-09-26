"""Web estática sin dependencias remotas, renderizada desde marts validados."""

import json
from pathlib import Path


def render(release: Path, tables: dict, status: dict):
    payload = json.dumps(
        {
            "rows": tables["mart_continuity"],
            "quality": tables["mart_quality"],
            "observations": status["observations"],
            "run_id": status["run_id"],
            "context": tables["mart_national_context"],
            "digital": tables["mart_digital_evidence"],
            "sources": tables["mart_source_coverage"],
            "total": status["total_observations"],
            "families": status["source_families"],
        },
        ensure_ascii=False,
    ).replace("<", "\\u003c")
    base = Path(__file__).parent
    template = (base / "report_template.html").read_text(encoding="utf-8")
    template = template.replace(
        "Proyecto de portfolio · v1.0", "Observatorio abierto · v2.0"
    )
    template = template.replace(
        "Cómo cambia la continuidad escolar entre provincias y años. Un observatorio con datos oficiales, contexto metodológico y trazabilidad hasta la celda de origen.",
        "Trayectorias escolares, acceso digital y evidencia sobre el uso de pantallas e inteligencia artificial. Datos públicos con poblaciones, límites y procedencia visibles.",
    )
    nav = (
        '<nav class="webnav" aria-label="Secciones">'
        + "".join(
            f'<button class="navbtn" data-panel="{id}" aria-pressed="{str(i == 0).lower()}">{label}</button>'
            for i, (id, label) in enumerate(
                [
                    ("continuity", "01 · Continuidad"),
                    ("national", "02 · Contexto"),
                    ("digital", "03 · Redes e IA"),
                    ("evidence", "04 · Evidencia PISA"),
                    ("pipeline", "05 · Pipeline y fuentes"),
                ]
            )
        )
        + '</nav><section id="continuity" class="panel">'
    )
    template = template.replace("</header>", "</header>" + nav, 1)
    template = template.replace(
        "<footer>",
        "</section>" + (base / "context_template.html").read_text() + "<footer>",
        1,
    )
    css = """[hidden]{display:none!important}.webnav{display:flex;flex-wrap:wrap;gap:8px;margin:32px 0;border-bottom:1px solid var(--line);padding-bottom:16px}.navbtn{border:1px solid var(--line);background:transparent;color:var(--ink);border-radius:25px;padding:11px 15px;cursor:pointer;font:600 13px system-ui}.navbtn[aria-pressed=true]{background:var(--ink);color:white}.navbtn:focus-visible{outline:3px solid #b66b43;outline-offset:3px}.section-title{margin:30px 0}.section-title h2{font-size:36px;margin-top:10px}.barrow{margin:18px 0;font-size:13px}.barrow strong{float:right}.track{height:7px;background:#e5eae1;border-radius:5px;margin-top:8px;overflow:hidden}.track span{height:100%;display:block;background:#096b5c}#distraction{display:grid;grid-template-columns:1fr 1fr;gap:35px}#metric{max-width:480px;width:100%;min-width:0}select{max-width:100%}.filters label{max-width:100%}#kidsTable td:first-child{min-width:220px}#kidsTable td:nth-child(3){min-width:220px}@media(max-width:800px){#distraction{grid-template-columns:1fr}.card{min-width:0;padding:17px}.section-title h2{font-size:28px}.webnav{gap:6px}.navbtn{padding:10px;font-size:12px}}"""
    template = template.replace("</style>", css + "</style>")
    template = template.replace(
        "</script>", "\n" + (base / "context_web.js").read_text() + "\n</script>"
    )
    (release / "dashboard.html").write_text(
        template.replace("__PAYLOAD__", payload), encoding="utf-8"
    )
