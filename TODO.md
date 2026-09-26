# Evolución priorizada

| Prioridad | Mejora | Habilidad demostrada | Criterio de aceptación |
|---|---|---|---|
| 1 | Publicación Snowflake por esquemas de release | Despliegue y consistencia de datos | Un fallo de dbt no altera ninguna tabla de la versión consumida; rollback probado |
| 2 | Observabilidad: frescura, volumen, duración y alertas | Operación y confiabilidad | Una fuente atrasada o caída genera una alerta reproducible con runbook |
| 3 | Almacenamiento de snapshots en objetos y retención | Ciclo de vida e infraestructura | Replay desde otra máquina con hashes verificados y política de retención probada |
| 4 | Infraestructura como código y entornos separados | Automatización cloud y acceso mínimo | Desarrollo y producción aislados; plan revisable sin credenciales en estado público |
| 5 | Detección de revisiones y carga incremental justificada | Diseño de procesamiento | Prueba con corrección histórica demuestra equivalencia con full rebuild y mide el ahorro |
| 6 | Linaje interoperable y contratos versionados | Gobierno de datos | Cambio incompatible detectado en CI y trazabilidad fuente → mart consultable |
| 7 | QA visual escritorio/móvil del reporte publicado | Entrega de productos de datos | Navegación y descargas verificadas en resoluciones definidas; versión visible |

Mantener el foco en garantías y evidencia. Kafka o Spark sólo serían justificables con un caso real de streaming o volumen; no aportan por sí solos a este dataset. La incorporación de nuevas fuentes debe respetar granularidad, licencias y denominadores.
