# Fuentes y referencias

Consulta y descarga inicial: 19 de septiembre de 2026. Verificación de la entrega local: 25 de septiembre de 2026 (Argentina). No se afirma que el snapshot sea la última revisión disponible después de esa descarga.

## Datos oficiales

Página de entrada: https://www.argentina.gob.ar/educacion/evaluacion-e-informacion-educativa/indicadores

- Abandono: https://www.argentina.gob.ar/sites/default/files/2018/04/tasa_de_abandono_interanual.zip
- Promoción: https://www.argentina.gob.ar/sites/default/files/2018/04/tasa_de_promocion_efectiva.zip
- Repitencia: https://www.argentina.gob.ar/sites/default/files/2018/04/tasa_de_repitencia.zip
- Documentación metodológica adicional: https://www.argentina.gob.ar/sites/default/files/2018/04/documentos_metodologicos_3.10.zip

Productor: Secretaría de Educación de la Nación; Relevamientos Anuales, Red Federal de Información Educativa. Los nombres institucionales de las hojas varían por período. Citar también el período analizado y la fecha de descarga.

La evidencia metodológica utilizada directamente está en la hoja `Limitaciones` y las notas al pie de cada libro provincial; se conserva en `reports/current/source_notes.json`. La nota del período 2024 documenta el cambio operativo bonaerense. El ZIP metodológico adicional está guardado como referencia; no interviene en las transformaciones ni se afirma haber procesado sus PDF.

`reports/current/sources.json` contiene los hashes íntegros, miembros seleccionados a nivel de observación y timestamps de la descarga. La reproducibilidad se apoya en esos archivos, no en que una URL oficial mantenga eternamente el mismo contenido.

## Documentación técnica consultada

- DuckDB + dbt: https://duckdb.org/2025/04/04/dbt-duckdb
- Airflow DAGs: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html
- Airflow 3.1.5: https://airflow.apache.org/docs/apache-airflow/3.1.5/
- dbt Snowflake: https://docs.getdbt.com/docs/core/connect-data-platform/snowflake-setup
- Snowflake dbt: https://docs.snowflake.com/en/user-guide/tutorials/dbt-projects-on-snowflake-getting-started-tutorial

Las versiones ejecutadas están fijadas en `uv.lock` y documentadas en `docs/VALIDACION.md`; una documentación `stable` puede describir una versión posterior.

## Ampliación multifuente v2

- Banco Mundial, API WDI: https://api.worldbank.org/v2/ — URLs completas por artefacto en `config/context_sources.json`; definiciones originales en `reports/current/wdi_metadata.json`. Productores UNESCO UIS e ITU.
- OECD, PISA 2022 volumen II, anexos: https://www.oecd.org/en/publications/pisa-2022-results-volume-ii_a97db61c-en/full-report/component-18.html . Planillas oficiales: https://stat.link/d5rsh2 y https://stat.link/pyhr6e . Metodología y contexto: https://www.oecd.org/en/publications/pisa-2022-results-volume-ii_a97db61c-en/full-report/component-12.html .
- UNICEF / UNESCO, Kids Online Argentina: https://www.unicef.org/argentina/informes/kids-online-ninios-ninias-adolescentes-conectados . Informe y resumen archivados con hashes y páginas; publicación 2025, trabajo de campo 2024.

Ver `docs/CONTEXTO_DIGITAL.md` para universos, incertidumbre y limitaciones. El catálogo de 16 artefactos se publica en `reports/current/source_catalog.json` y `exports/mart_source_coverage.csv`.
