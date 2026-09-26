# Snowflake: integración ejecutada

Validada el 26/09/2026, ejecución `20260926T180439_snowflake_e4ed67`. Tres tablas raw (15.795 + 974 + 16 filas), 13 modelos y 41 pruebas dbt aprobadas. Once tablas exportables comparadas con DuckDB, tolerancia numérica 1e-9. La web se construye desde los resultados leídos a Snowflake, no desde fixtures.

## Recursos y autenticación

- Base TRAYECTORIAS_AR; esquemas RAW y ANALYTICS.
- Usuario SERVICE TRAYECTORIAS_PIPELINE, rol TRAYECTORIAS_ROLE limitado a recursos del proyecto, autenticación RSA.
- Warehouse TRAYECTORIAS_WH, X-Small, autosuspensión 60 segundos, timeout de sentencia 300 segundos.
- Monitor TRAYECTORIAS_TEST_MONITOR: cuota 1 crédito, frecuencia NEVER, suspensión inmediata al 100%. El monitor no limita almacenamiento ni garantiza gasto exacto; no elevar cuota automáticamente.

La clave pública del usuario de servicio se registra mediante SQL con un rol administrador. La privada y connection.json se guardan fuera del repositorio en `~/.config/trayectorias/snowflake/`. Permisos 600 para archivos sensibles y 700 para directorio. No se almacena la contraseña personal ni se altera su MFA. El backup no contiene claves ni configuración de autenticación.

## Ejecutar

```bash
uv sync --frozen --extra dev --extra snowflake --python 3.13
.venv/bin/python scripts/run_snowflake.py
node scripts/check_web.cjs reports/snowflake/current
```

En una instalación nueva: ejecutar `infra/snowflake.sql` con un rol administrador; generar una clave con `.venv/bin/python scripts/prepare_snowflake_key.py --account ORGANIZACION-CUENTA`; ejecutar el `registrar_pipeline.sql` generado en el directorio externo. El runner requiere primero una ejecución local correcta de `make run`. No regenerar claves para cada ejecución. No incluir claves dentro de la imagen Docker.

El runner lee la configuración externa, carga snapshots locales validados, corre dbt, compara las once tablas con reports/current y publica web/CSV/Parquet y una copia DuckDB para consulta offline. La salida está en reports/snowflake/current. Con el contenedor report activo: http://127.0.0.1:8080/snowflake/current/dashboard.html . Abrir esta web estática no ejecuta consultas Snowflake.

## Garantías y límites

El loader reemplaza OBSERVATIONS, CONTEXT_OBSERVATIONS y SOURCE_CATALOG mediante DELETE/INSERT en una transacción; valida conteo y unicidad antes de COMMIT. DDL de creación ocurre antes de BEGIN. Raw y los modelos dbt son pasos separados: no hay publicación atómica de todos los modelos cloud. La web y los exports se publican sólo al terminar dbt y la comparación.

El runner comparte el lock local con el pipeline DuckDB. No hay coordinación distribuida: no ejecutar desde dos equipos a la vez. El despliegue Docker validado ejecuta DuckDB; la ruta cloud validada ejecuta Python/dbt en el host.

Los errores quedan en reports/snowflake/runs/<id>. Un error no reemplaza la web cloud anterior. Después de corregir, repetir el runner dentro de la cuota configurada. Si se agota, revisar el presupuesto antes de cambiarla. El código no activa programación recurrente.

## Consumo observado

Warehouse verificado SUSPENDED después de la ejecución. Snowsight con ACCOUNTADMIN mostró monitor de nivel WAREHOUSE, cuota 1, consumo redondeado 0,05 y remanente 0,95. Es una lectura del monitor, no una factura final. Las comprobaciones administrativas quedan en el entorno local; no se publican identificadores de cuenta ni capturas de sesiones.

Referencias: [monitor de recursos](https://docs.snowflake.com/en/sql-reference/sql/create-resource-monitor), [límites del monitor](https://docs.snowflake.com/en/user-guide/resource-monitors), [autenticación por clave](https://docs.snowflake.com/en/user-guide/key-pair-auth), [perfil dbt Snowflake](https://docs.getdbt.com/docs/core/connect-data-platform/snowflake-setup).
