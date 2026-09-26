"""Genera diagramas SVG y evidencia pública con una lista explícita de campos."""

import json
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs/assets"


def diagram(name, number, title, subtitle, cards, footer):
    parts = [
        f'''<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="900" viewBox="0 0 1440 900" role="img" aria-label="{escape(title)}">
<rect width="1440" height="900" fill="#101c2a"/>
<rect x="56" y="54" width="56" height="6" fill="#52dbc0"/>
<g font-family="DejaVu Sans, sans-serif">
<text x="56" y="99" fill="#52dbc0" font-size="18" letter-spacing="3">TRAYECTORIAS AR / INGENIERÍA DE DATOS / {number}</text>
<text x="56" y="160" fill="#ffffff" font-size="42" font-weight="bold">{escape(title)}</text>
<text x="56" y="202" fill="#b7c8da" font-size="20">{escape(subtitle)}</text>'''
    ]
    for i, (heading, lines) in enumerate(cards):
        x = 56 + (i % 3) * 446
        y = 250 + (i // 3) * 265
        parts.append(
            f'<rect x="{x}" y="{y}" width="426" height="240" rx="16" fill="#1b2d40" stroke="#34516b"/>'
        )
        parts.append(
            f'<text x="{x + 22}" y="{y + 37}" fill="#52dbc0" font-size="16">0{i + 1}</text>'
        )
        parts.append(
            f'<text x="{x + 22}" y="{y + 75}" fill="#fff" font-size="23" font-weight="bold">{escape(heading)}</text>'
        )
        for j, line in enumerate(lines):
            parts.append(
                f'<text x="{x + 22}" y="{y + 114 + j * 28}" fill="#d1deeb" font-size="17">{escape(line)}</text>'
            )
    parts.append(
        f'<text x="56" y="837" fill="#96b0c8" font-size="17">{escape(footer)}</text></g></svg>'
    )
    (ASSETS / name).write_text("\n".join(parts), encoding="utf-8")


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    diagram(
        "01-arquitectura.svg",
        "01",
        "De la publicación oficial al producto de datos",
        "Dos motores de ejecución, contratos compartidos y procedencia conservada.",
        [
            (
                "Fuentes oficiales",
                [
                    "Educación · WDI · PISA · Kids",
                    "ZIP / XLSX / JSON / PDF",
                    "4 familias · 16 artefactos",
                ],
            ),
            (
                "Snapshots + contratos",
                [
                    "HTTPS → SHA-256 → manifiestos",
                    "Cobertura, esquema y tipos",
                    "Celda / posición JSON / página",
                ],
            ),
            (
                "Warehouse",
                [
                    "3 tablas raw → 13 modelos dbt",
                    "DuckDB local / Snowflake cloud",
                    "Hechos con distinto universo",
                ],
            ),
            (
                "Controles de calidad",
                [
                    "31 pruebas Python · 41 dbt",
                    "Replay con igualdad de contenido",
                    "11 tablas comparadas entre motores",
                ],
            ),
            (
                "Publicación de release",
                [
                    "Versión aislada → validar → publicar",
                    "Puntero local reemplazado al final",
                    "Fallo: conservar última versión",
                ],
            ),
            (
                "Consumo + operación",
                [
                    "Web HTML/JS · CSV · Parquet",
                    "Airflow · Docker · GitHub Actions",
                    "Logs y manifiestos por ejecución",
                ],
            ),
        ],
        "Diagrama documental. La atomicidad de publicación local no implica atomicidad conjunta de modelos cloud.",
    )
    diagram(
        "02-contratos.svg",
        "02",
        "Investigar antes de integrar",
        "Cada formato exige un contrato; cada porcentaje necesita un universo.",
        [
            (
                "Educación / ZIP + Excel",
                [
                    "15.795 celdas normalizadas",
                    "27 ámbitos · 13 transiciones",
                    "Nulos y tasas fuera de rango",
                ],
            ),
            (
                "WDI / API JSON",
                [
                    "832 combinaciones esperadas",
                    "647 valores + 185 nulos",
                    "8 metadatos y año observado",
                ],
            ),
            (
                "PISA / Excel",
                [
                    "120 estimaciones",
                    "Categorías y error estándar",
                    "Asociación ≠ efecto causal",
                ],
            ),
            (
                "Kids Online / PDF",
                [
                    "22 estimaciones revisadas",
                    "Hash de edición + ancla de página",
                    "Población y denominador explícitos",
                ],
            ),
            (
                "Validar procedencia",
                [
                    "Productor → formato → cobertura",
                    "Referencia ≠ publicación ≠ descarga",
                    "Cambios incompatibles: detener",
                ],
            ),
            (
                "Conservar límites",
                [
                    "No imputar encuestas a provincias",
                    "No rellenar huecos con ceros",
                    "No desactivar TLS para descargar",
                ],
            ),
        ],
        "Las observaciones son agregadas. Los 16 artefactos no equivalen a 16 estudios independientes.",
    )
    diagram(
        "03-warehouse.svg",
        "03",
        "Modelo del warehouse y rutas de linaje",
        "Las flechas se leen dentro de cada tarjeta; ambos dominios preservan su propio grano.",
        [
            (
                "Entrada educativa",
                ["raw.observations", "→ stg_observations", "→ int_transitions"],
            ),
            (
                "Dimensiones + hecho",
                [
                    "dim_geography / dim_period",
                    "dim_indicator",
                    "→ fct_education_rates",
                ],
            ),
            (
                "Marts educativos",
                ["fct_education_rates", "→ mart_continuity", "→ mart_quality"],
            ),
            (
                "Entrada de contexto",
                [
                    "raw.context_observations",
                    "→ fct_context_indicators",
                    "→ dim_context_indicator",
                ],
            ),
            (
                "Marts de contexto",
                [
                    "fct_context_indicators",
                    "→ mart_national_context",
                    "→ mart_digital_evidence",
                ],
            ),
            (
                "Procedencia transversal",
                [
                    "raw.source_catalog + hechos",
                    "→ mart_source_coverage",
                    "URL · SHA-256 · localizador",
                ],
            ),
        ],
        "Educación: año × geografía × nivel × grado × indicador. Contexto: país × año × indicador × subgrupo × categoría.",
    )
    diagram(
        "04-operacion.svg",
        "04",
        "Publicar sólo una versión completa",
        "Airflow: preflight → build_release → verify_release. Un proceso conserva el lock durante la construcción.",
        [
            (
                "Preflight",
                [
                    "Verificar entorno y configuración",
                    "Fuentes disponibles / modo offline",
                    "DAG: máximo una ejecución activa",
                ],
            ),
            (
                "Construir",
                [
                    "Capturar → normalizar → cargar",
                    "dbt build → catálogo → exportar",
                    "Logs y run.json por intento",
                ],
            ),
            (
                "Validar",
                [
                    "Contratos Python + tests SQL",
                    "Contenido y enlaces de la web",
                    "Cloud: comparación con DuckDB",
                ],
            ),
            (
                "Publicar",
                [
                    "Reemplazar reports/current",
                    "Web + warehouse + exports",
                    "Lock local para excluir escritores",
                ],
            ),
            (
                "Si ocurre un fallo",
                [
                    "No mover el puntero publicado",
                    "Retener logs del intento",
                    "Corregir causa antes de reintentar",
                ],
            ),
            (
                "Recuperar",
                [
                    "Reusar manifiestos del release",
                    "Verificar hashes de snapshots",
                    "Replay offline y control final",
                ],
            ),
        ],
        "Calendario mensual configurado; scheduler persistente pendiente. El lock actual no coordina equipos distintos.",
    )
    local = json.loads((ROOT / "reports/current/run.json").read_text())
    cloud = json.loads((ROOT / "reports/snowflake/current/run.json").read_text())

    def summary(run):
        results = run["dbt_results"]
        return {
            **{
                k: run[k]
                for k in ("run_id", "status", "total_observations", "dataset_sha256")
            },
            "models": sum(r["id"].startswith("model.") for r in results),
            "tests": sum(r["id"].startswith("test.") for r in results),
            "all_results_successful": all(
                r["status"] in ("pass", "success") for r in results
            ),
        }

    evidence = {
        "description": "Resumen de ejecuciones, sin configuración de cuenta ni logs.",
        "local": summary(local),
        "snowflake": summary(cloud),
        "comparison": cloud["comparison"],
        "source_hashes": local["sources_sha256"],
        "limits": [
            "CI: consultar Actions",
            "QA visual de escritorio/móvil pendiente",
            "Docker y Snowflake validados antes de la revisión documental; ver VALIDACION.md",
        ],
    }
    (ROOT / "docs/evidence/validation.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n"
    )
    diagram(
        "05-validacion.svg",
        "05",
        "Garantías respaldadas por ejecuciones",
        "Snapshot validado en septiembre de 2026. CI remota: consultar el badge y los logs de GitHub Actions.",
        [
            (
                "Python",
                [
                    "31 pruebas aprobadas",
                    "Contratos, fallos y concurrencia",
                    "Huella de código sin artefactos",
                ],
            ),
            (
                "dbt",
                [
                    "13 modelos · 41 pruebas",
                    "Claves, relaciones y semántica",
                    "Resultados de build conservados",
                ],
            ),
            (
                "Reproducibilidad",
                [
                    "16.769 observaciones",
                    "Mismos snapshots → mismo dataset",
                    "16 hashes de fuentes verificados",
                ],
            ),
            (
                "Snowflake",
                [
                    "Ejecución real con clave de servicio",
                    "11 tablas equivalentes a DuckDB",
                    "Tolerancia numérica: 1e-9",
                ],
            ),
            (
                "Docker + Airflow",
                [
                    "Imagen y replay offline ejecutados",
                    "DAG probado en entorno separado",
                    "Sin scheduler productivo activo",
                ],
            ),
            (
                "Web + límites",
                [
                    "Filtros y enlaces: pruebas jsdom",
                    "QA visual completo pendiente",
                    "Datos públicos agregados",
                ],
            ),
        ],
        "Evidencia: docs/evidence/validation.json. Síntesis documental; no es una captura de las interfaces de ejecución.",
    )


if __name__ == "__main__":
    main()
