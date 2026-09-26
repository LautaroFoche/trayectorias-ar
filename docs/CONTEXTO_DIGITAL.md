# Contexto educativo y digital: contrato y metodología v2

## Fuentes y granularidad

- **WDI**: API del Banco Mundial, ocho indicadores, cuatro países, años 2000–2025. Productores primarios UNESCO UIS para educación e ITU para conectividad, con definiciones originales preservadas en `wdi_metadata.json`. El contrato exige 832 combinaciones, incluso las que tienen valor nulo. Rechaza paginación incompleta, duplicados, países inesperados y valores inválidos. No rellena huecos. Ver `config/wdi_indicators.json`.
- **PISA**: Excel originales enlazados desde anexos OECD, capítulos 3 y 5 del volumen II de PISA 2022. Extrae tablas II.B1.3.9, II.B1.5.64, II.B1.5.65 y II.B1.5.67; valida encabezados, escala, propósito y países. Retiene celdas de valor y error estándar. Estudiantes escolarizados de 15 años; estimaciones ponderadas, no datos individuales.
- **Kids Online**: PDF completo y resumen ejecutivo UNICEF/UNESCO. Extracción editorial de 22 estimaciones en `config/kids_reviewed.json`. El pipeline valida hash del PDF y un ancla textual por página. No es una extracción automática universal de tablas PDF: agregar indicadores requiere leer y revisar valor, universo y denominador. El hash fija exactamente la edición revisada; si cambia, la descarga falla hasta nueva revisión documentada.

Las fuentes de contexto tienen granularidad país/año/indicador/subgrupo/categoría. No se unen a provincias. Las tablas educativas existentes mantienen su propia granularidad y reglas de comparabilidad.

## Indicadores WDI

| Código | Significado |
|---|---|
| SE.XPD.TOTL.GD.ZS | Gasto público educativo / PIB |
| SE.XPD.TOTL.GB.ZS | Gasto educativo / gasto público |
| SE.SEC.ENRR | Matrícula bruta secundaria |
| SE.PRM.ENRR | Matrícula bruta primaria |
| SE.PRM.ENRL.TC.ZS | Alumnos por docente en primaria |
| SE.SEC.CMPT.LO.ZS | Finalización de secundaria inferior |
| IT.NET.USER.ZS | Personas que usan Internet |
| IT.NET.BBND.P2 | Suscripciones de banda ancha fija por 100 habitantes |

No confundir matrícula bruta con cobertura neta, finalización de secundaria inferior con egreso de toda la secundaria, ni suscripciones con personas. La última observación varía por país/indicador. Argentina tiene alumnos/docente sólo hasta 2008 en este snapshot; la web avisa el rezago.

## Kids Online: denominadores que deben conservarse

Relevamiento octubre–diciembre de 2024; publicación 2025. Universo: estudiantes de 9–17 años en ciudades de al menos 50.000 habitantes; 5.910 participantes, 291 escuelas. Las estimaciones por edad y NSE son subgrupos; no sumarlos.

- 58% utilizó ChatGPT alguna vez; edades 9–11: 37%, 12–14: 56%, 15–17: 74%; NSE bajo: 42%, alto: 75%.
- 66% de quienes usaron ChatGPT (base 3.416) lo usó para tareas. 69% de los usuarios escolares lo encontró muy útil. Esta última base no se reconstruye multiplicando porcentajes.
- 46% identificó al menos un uso problemático. Dentro de ese grupo: 50% percibió menor rendimiento; 47% intentó reducir tiempo sin éxito; 38% reportó dificultades de alimentación/sueño; 26% conflictos. No extrapolar esos porcentajes al total. No se conoce aquí el tamaño muestral exacto del grupo condicionado.
- 80% redes diariamente o casi diariamente; 94% videos; 61% usos escolares. 21% experimentó maltrato online de compañeros de escuela.

Son autorreportes y porcentajes publicados redondeados. No se dispone de errores estándar en esta extracción. `sample_n` es el tamaño muestral reportado, no una población expandida ni un denominador que permita reconstruir conteos ponderados. `null` significa que no se incorporó un tamaño confiable para ese subgrupo.

## PISA: incertidumbre y causalidad

Se incluyen ambos propósitos de uso —aprendizaje y ocio— y las siete categorías de duración. Las medias por categoría no ajustan por nivel socioeconómico. Las frecuencias de distracción conservan cuatro categorías: todas, mayoría, algunas y nunca/casi nunca.

El coeficiente continuo de ocio se conserva con y sin ajuste por ESCS de estudiante y escuela. La web destaca el ajustado: Argentina ≈ +0,50 puntos por hora, EE ≈ 0,74; intervalo normal aproximado del 95% ≈ [-0,95; 1,95]. Es compatible con cero. No se generalizan los coeficientes negativos de otros países a Argentina.

`ci95_low/high = value ± 1.96 * standard_error`. Son aproximaciones normales para visualización, no una réplica del diseño muestral ni una prueba de diferencias entre categorías. No se infieren errores de porcentajes sumados, porque falta su covarianza. No se interpretan asociaciones como efectos causales ni percepciones como notas efectivamente medidas.

## Modelos y trazabilidad

`raw.context_observations` → `fct_context_indicators` → `mart_national_context` / `mart_digital_evidence`; `dim_context_indicator` describe cada indicador por fuente. `raw.source_catalog` se une sólo por procedencia para `mart_source_coverage`.

Campos: ID determinista, fuente, país, año de referencia y publicación, indicador, unidad, población, subgrupo, categoría y orden, valor, error estándar, estado de valor, marca original, tipo de evidencia, denominador, N muestral, nota, localizador, hash, URL y método de extracción.

Los 16 artefactos representan cuatro familias editoriales, no 16 fuentes estadísticas independientes. Ocho son metadatos. Los dos PDF Kids pertenecen al mismo estudio y las dos planillas PISA al mismo relevamiento.

## Actualización

`make run` vuelve a consultar las fuentes. No garantiza que todos los organismos hayan publicado el año actual. Para extender 2000–2025, modificar conjuntamente URL, contrato de años, prueba de cobertura y controles de la web. Para cambiar PDF, revisar la edición y actualizar hash, valores y anclas juntos. `make offline` reproduce las fuentes ya capturadas.

No se incorporó ENACOM: no se pudo validar la cadena TLS del recurso explorado. No se desactivó la verificación de certificados. No se agregaron datos sintéticos ni fuentes sin verificación para cubrir esa ausencia.
