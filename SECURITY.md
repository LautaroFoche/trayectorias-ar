# Seguridad

## Alcance público

Se publica código, configuración de fuentes públicas, diagramas y resúmenes agregados de validación. No se versionan snapshots de terceros, bases de datos, logs operativos, archivos `.env`, claves ni configuración de cuentas. Las observaciones procesadas son agregadas; no hay registros individuales de estudiantes.

## Credenciales y ejecución

Snowflake utiliza un usuario de servicio con rol limitado al proyecto. La clave privada y `connection.json` residen fuera del repositorio, con permisos 600 y directorio 700. La infraestructura requiere un administrador sólo para aprovisionar; el pipeline usa el rol del proyecto. Nunca copiar claves a una imagen Docker, un issue, un log público o un artefacto de Actions.

Las descargas mantienen verificación TLS. Las fuentes y los identificadores SQL configurables tienen validación; las descargas se limitan en tamaño y tiempo. Los servidores de demostración se enlazan a localhost. GitHub Actions tiene permisos de lectura y no recibe credenciales Snowflake.

## Antes de publicar artefactos

Revisar el contenido real, además de `.gitignore`: éste no elimina secretos ya incorporados al historial. No subir respaldos locales ni capturas de sesiones administrativas. El resumen `docs/evidence/validation.json` se construye por lista de campos permitidos; no copia manifiestos de autenticación ni mensajes de error.

Esta revisión no sustituye una auditoría de seguridad especializada. Para reportar una vulnerabilidad, usar el reporte privado de GitHub si está habilitado; no incluir credenciales en issues públicos. Ante una exposición, revocar primero la credencial y luego sanear el historial y los artefactos.

## Revisión de publicación

Se analizó el árbol público con Gitleaks 8.30.1 y se revisaron referencias a cuentas, correos personales, rutas privadas y archivos sensibles. El escaneo no detectó secretos. Se publica una raíz de historial saneada; el historial operativo anterior queda como respaldo local, sin enviarse al remoto. Un resultado sin hallazgos no garantiza ausencia absoluta de vulnerabilidades.
