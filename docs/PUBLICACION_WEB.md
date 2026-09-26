# Reporte público en GitHub Pages

URL: https://lautarofoche.github.io/trayectorias-ar/

El workflow `.github/workflows/ci.yml` ejecuta el pipeline con fuentes oficiales, verifica replay y pruebas web, empaqueta el sitio y lo despliega cuando los jobs `quality` y `airflow` terminan correctamente. Sólo `main` puede desplegar; los pull requests validan el paquete sin publicarlo.

## Contenido público

`scripts/build_pages.py` genera `reports/pages/` desde un release exitoso. Incluye `index.html`, `dashboard.html`, once tablas CSV/Parquet y tres JSON públicos: `run.json`, `sources.json` y `source_catalog.json`. Los JSON se seleccionan por campos permitidos. No se copian logs, bases DuckDB, snapshots originales, configuración de autenticación ni documentación operativa local. No se sube `reports/` completo.

La web usa datos embebidos y enlaces relativos para funcionar bajo `/trayectorias-ar/`. No necesita cuenta, backend ni consultas Snowflake al navegar. El año de referencia del dato y la ejecución visible pueden ser diferentes.

## Actualización y recuperación

Un push a `main` o una ejecución manual de Actions construye una nueva versión. No se configuró una actualización por calendario. Si falla una fuente, un contrato o una prueba, no se ejecuta el despliegue y la web conserva la publicación anterior. Revisar los logs de Actions antes de reintentar; no relajar contratos para ocultar fallos.

GitHub Pages se configura con origen `workflow`. El job de despliegue tiene permisos `pages: write` e `id-token: write`; los jobs de validación sólo necesitan lectura del repositorio. No se configuraron secretos Snowflake en Actions.

Para revisar localmente:

```bash
.venv/bin/python scripts/build_pages.py --output /tmp/trayectorias-pages-preview
node scripts/check_web.cjs /tmp/trayectorias-pages-preview
```

El directorio de salida debe ser nuevo para evitar arrastrar archivos de otra ejecución.

Referencia: [workflows personalizados de GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
