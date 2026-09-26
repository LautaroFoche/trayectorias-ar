# Publicación para LinkedIn

## Texto listo para copiar

Construí TrayectoriasAR, un proyecto de ingeniería de datos con fuentes públicas sobre educación argentina y contexto digital.

El desafío fue convertir ZIP/Excel, API JSON y PDF en datos reproducibles, con contratos claros y trazabilidad hasta la celda o página de origen.

El pipeline integra 4 familias de fuentes y 16.769 observaciones agregadas. Implementé snapshots con SHA-256, normalización en Python, un warehouse con SQL/dbt, pruebas de calidad y publicación de una web con exportaciones CSV y Parquet.

Lo validé con DuckDB y Snowflake: 13 modelos dbt, 41 pruebas y comparación de 11 tablas entre ambos motores. También incorporé Docker, un DAG de Airflow y un workflow de GitHub Actions.

Una decisión central: si falla una validación, la web conserva la última versión correcta. Otra: mantener separados los universos de las fuentes para no producir relaciones estadísticas que los datos no permiten sostener.

El repositorio incluye arquitectura, investigación, contratos, pruebas, instrucciones de reproducción y límites actuales. Es una demostración de ingeniería; el siguiente paso es fortalecer observabilidad y publicación de versiones en cloud.

Repositorio: https://github.com/LautaroFoche/trayectorias-ar

#DataEngineering #Python #SQL #dbt #Snowflake #Airflow #Docker #DatosAbiertos

## Material de acompañamiento

Adjuntar `docs/assets/portfolio-linkedin.png` como imagen principal. Los SVG del README permiten recorrer arquitectura, contratos, warehouse, operación y validación. Son diagramas del proyecto, no capturas de consolas.

Antes de publicar: comprobar el badge de CI y revisar que el texto refleje los resultados actuales. No adjuntar archivos de autenticación, respaldos completos ni capturas administrativas. Este documento es un borrador; no publica mensajes en LinkedIn.
