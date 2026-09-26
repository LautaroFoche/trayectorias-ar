# Evidencia de validación

## Alcance de las ejecuciones

Se conserva una síntesis pública en [evidence/validation.json](evidence/validation.json). Sus campos se seleccionan explícitamente; no incluye perfiles de cuenta, claves, logs administrativos ni rutas privadas. Los artefactos completos se generan localmente bajo `reports/` y no se versionan.

| Control | Resultado verificado |
|---|---|
| Pruebas Python | 31 aprobadas, incluidas dos pruebas del paquete público |
| dbt build local | 13 modelos y 41 pruebas aprobados |
| Replay offline | Mismo hash normalizado y hashes de los 16 artefactos |
| Docker | Imagen construida y pipeline offline ejecutado; release `20260926T175307_a2643475` |
| Airflow 3.1.5 | DAG de tres tareas ejecutado; sin scheduler persistente |
| Snowflake | Release `20260926T180439_snowflake_e4ed67`; 13 modelos y 41 pruebas aprobados |
| Comparación entre motores | 11 tablas equivalentes con tolerancia numérica `1e-9` |
| Web | Pruebas jsdom de filtros, nulos, rezago, denominadores y enlaces |

Hash de contenido: `b4b723f8eff196e2fa6ea6a217c246303d949f0b2f2cefec676baff15dc03c17`.

Educación: 15.795 observaciones, incluidas 1.014 celdas no aplicables y 1.042 tasas fuera del rango teórico conservadas. WDI: 832 combinaciones, 647 con valor y 185 nulas. PISA: 120 estimaciones. Kids Online: 22 estimaciones revisadas. Total: 16.769 observaciones agregadas, no personas.

## Revisión para publicación

Se corrigieron comentarios obsoletos y la versión del proyecto dbt. La huella del código incluye nombres de archivos y excluye artefactos generados. `dbt/build_results.json` conserva los resultados de construcción antes de generar el catálogo. Se uniformó el formato Python y se revisaron importaciones y referencias. Se separó el material operativo local del árbol público y se preparó un historial público independiente.

Docker y Snowflake fueron validados antes de esos ajustes de instrumentación y presentación. El replay local se repitió después; no se afirma una nueva ejecución cloud de cada cambio documental. Los modelos SQL de transformación no se modificaron durante esa revisión.

## Reproducir controles

```bash
make test
make run
.venv/bin/python scripts/check_reproducibility.py
npm ci --ignore-scripts
npm run test:web
make airflow-check
```

El pipeline guarda `run.json`, logs, manifiestos y resultados dbt en el directorio del release. Comparar `dataset_sha256` entre ejecuciones; los timestamps y los archivos binarios pueden diferir. Los hashes identifican un snapshot, no garantizan que la fuente nunca cambie.

## Límites

Consultar [GitHub Actions](https://github.com/LautaroFoche/trayectorias-ar/actions) para el estado remoto actual. Las pruebas del DOM no sustituyen QA visual de escritorio y móvil, aún pendiente. La web se publica mediante GitHub Pages; no hay scheduler productivo. La comparación cloud se validó sobre estos datos; no constituye una garantía universal de equivalencia entre motores.

Los diagramas de `docs/assets/` son ilustraciones documentales, no capturas. Se generan con `python scripts/build_portfolio_assets.py` en el entorno con las ejecuciones local y cloud disponibles. La imagen para LinkedIn se obtiene con ImageMagick: `magick docs/assets/01-arquitectura.svg docs/assets/portfolio-linkedin.png`.
