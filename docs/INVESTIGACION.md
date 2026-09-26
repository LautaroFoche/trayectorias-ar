# Investigación y traducción a contratos de datos

## Pregunta inicial

¿Cómo organizar series de continuidad educativa argentina y contexto digital para que cada resultado se pueda auditar y reconstruir? La exploración temática orienta qué adquirir; la entrega principal es una plataforma pequeña de datos con garantías explícitas.

## Proceso

1. Localizar publicaciones institucionales y sus archivos originales, evitando agregadores sin procedencia verificable.
2. Inspeccionar formatos, hojas, notas metodológicas, unidades y cambios de definición antes de diseñar tablas.
3. Definir el grano y distinguir año de referencia, publicación y descarga.
4. Evaluar si la fuente admite actualización automática o necesita revisión editorial.
5. Convertir supuestos en contratos ejecutables y pruebas; conservar las limitaciones junto al dato.
6. Capturar snapshots con SHA-256 y documentar el localizador de cada observación.

## Decisiones por fuente

**Educación.** Tres ZIP con libros provinciales de abandono, promoción y repitencia. Las estructuras 6–6 y 7–5, nulos estructurales y notas por período requieren normalización específica. Se conserva el total nacional oficial; no se calcula un promedio provincial. Las tasas fuera de rango no se recortan. Se señalan la pandemia y el cambio bonaerense de 2024.

**WDI.** La API permite una adquisición reproducible, pero cobertura completa de combinaciones no significa valores observados completos. El contrato conserva 832 combinaciones y 185 nulos en el snapshot validado. Los ocho archivos de metadatos preservan definiciones y productores. Se diferencian matrícula bruta, finalización de secundaria inferior y suscripciones de banda ancha.

**PISA.** Se usan tablas originales del volumen II de 2022, con celdas de valor y error estándar. Las medias por categoría y coeficientes ajustados son objetos diferentes. Se conservan categorías y métodos; no se interpretan asociaciones observacionales como efectos causales.

**Kids Online.** Los PDF requieren curación: 22 estimaciones se registran en `config/kids_reviewed.json`, con página, ancla, población y denominador. El pipeline verifica la edición por hash. Un nuevo PDF exige revisión humana antes de actualizar la configuración. La automatización verifica la extracción aprobada; no pretende comprender cualquier PDF futuro.

## Exclusiones

ENACOM quedó fuera al no poder validar la cadena TLS del recurso explorado. Se mantuvo la verificación de certificados. No se incorporaron publicaciones sin procedencia, datos simulados para completar huecos, inferencias provinciales desde encuestas nacionales ni relaciones causales a partir de correlaciones.

## Resultado técnico

Dos dominios de hechos —educación y contexto— con catálogo de fuentes compartido. Cada fila conserva URL, hash y localizador: miembro/hoja/celda, posición JSON o página PDF. La reproducibilidad se define respecto de snapshots concretos; las URLs del productor pueden cambiar de contenido.

El detalle de URLs está en [FUENTES.md](FUENTES.md); la semántica de las variables y denominadores, en [DATOS.md](DATOS.md) y [CONTEXTO_DIGITAL.md](CONTEXTO_DIGITAL.md).
