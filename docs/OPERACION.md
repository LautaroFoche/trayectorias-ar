# Operación y recuperación

## Inicio y reanudación

Desde la raíz del repositorio, consultar `TODO.md` y `docs/VALIDACION.md`. Ejecutar `make setup` sólo si el entorno falta o cambió el lock. `make offline` reproduce las fuentes guardadas; `make run` consulta nuevamente las URLs y puede incorporar revisiones históricas.

La ejecución imprime eventos JSON y guarda `reports/runs/<run_id>/run.json`. Los manifiestos registran fechas de descarga; cada observación registra su año de referencia, distinto al timestamp del directorio. Una nueva ejecución offline no implica datos más recientes.

## Archivos de una versión

- `warehouse.duckdb`: esquemas raw y analytics.
- `dashboard.html`: reporte navegable, datos embebidos.
- `exports/`: once tablas, cada una en CSV y Parquet.
- `sources.json` y `context_sources.json`: URLs y hashes utilizados.
- `source_catalog.json`: catálogo unificado de 16 artefactos.
- `wdi_metadata.json`: definiciones originales de los ocho indicadores WDI.
- `source_notes.json`: notas conservadas de las hojas.
- `run.json`: estado, filas, períodos, hash del dataset y resultados dbt.
- `dbt/manifest.json`, `catalog.json`, `run_results.json`: linaje y evidencia.
- `build.log`, `docs_generate.log`: detalle de las ejecuciones.

El enlace `reports/current` señala la versión vigente. `data/warehouse.duckdb` señala al mismo warehouse. No editar datos ni archivos dentro de una versión publicada.

## Consultar

```bash
.venv/bin/python - <<'PY'
import duckdb
with duckdb.connect('data/warehouse.duckdb', read_only=True) as db:
    print(db.sql("""
        select year_from, geo_name, abandonment_pct, comparable_change_pp
        from analytics.mart_continuity
        where geo_code='14' and level='secundaria'
        order by year_from
    """))
PY
```

## Fallos esperados

| Síntoma | Qué hacer |
|---|---|
| HTTP 403/timeout | Revisar acceso a la URL oficial; usar `make offline` si hay snapshot validado. No reemplazar por datos inventados |
| Hash inválido | Recuperar el archivo cuyo hash figura en la versión vigente; nunca actualizar el hash para aceptar corrupción |
| Encabezado/hoja desconocida | Comparar el archivo nuevo con el anterior, revisar contrato y añadir un test antes de admitirlo |
| Cobertura incompleta | No quitar el control; investigar el cambio de publicación |
| dbt falla | Abrir el `build.log` del intento; la versión anterior sigue publicada |
| Ya hay un pipeline | Esperar a la ejecución activa; el bloqueo se libera al salir. No borrar versiones activas |
| Docker denegado | Usar la ruta local verificada o configurar acceso al daemon fuera del proyecto |

## Restaurar fuentes de la última versión válida

Si el manifiesto de ingesta quedó apuntando a una descarga rechazada, copiar `reports/current/sources.json` a `data/raw/manifest.json` y ejecutar `make offline`. Para las nuevas fuentes, copiar también `reports/current/context_sources.json` a `data/raw/context_manifest.json`. Todos los snapshots correspondientes deben seguir presentes. Esto reconstruye usando el código actual; no es una restauración de código.

Para restaurar exactamente una versión de publicación anterior, identificar primero una carpeta cuyo `run.json` tenga estado `success`. Cambiar el enlace mediante un enlace temporal y `os.replace` bajo el mismo bloqueo de escritura. Mantener la versión desplazada para recuperación. No automatizar borrados de snapshots: varias versiones pueden referenciarlos.

## Airflow

El entorno aislado evita mezclar restricciones de Airflow con dbt. `make airflow-test` crea/migra metadatos en `.airflow`, ejecuta un DAG manual offline y finaliza. No activa programación persistente.

Para una sesión local de demostración con interfaz, después de `make airflow-setup`:

```bash
export AIRFLOW_HOME="$PWD/.airflow"
export AIRFLOW__CORE__DAGS_FOLDER="$PWD/orchestration"
export AIRFLOW__CORE__LOAD_EXAMPLES=false
export TRAYECTORIAS_ROOT="$PWD"
export TRAYECTORIAS_OFFLINE=true
.airflow-venv/bin/airflow standalone
```

Usar únicamente como desarrollo local. Las credenciales de esa interfaz las genera Airflow. Para actualización remota real quitar el modo offline, activar el DAG y mantener sus procesos de scheduler/API/procesador. Esta sesión de desarrollo persistente no se dejó iniciada.

## CI y mantenimiento

El workflow hace pruebas unitarias y una integración con fuentes oficiales, seguida de replay offline. La integración puede fallar por indisponibilidad del productor: el fallo debe verse, no sustituirse por fixtures. Los datos y credenciales no se commitean. El paquete de entrega conserva snapshots para reproducción local.

La retención es manual: cada ejecución conserva base, documentación y exports. Para producción definir horizonte, backups y cuotas. El volumen actual es pequeño, pero repetir indefinidamente consume disco.
