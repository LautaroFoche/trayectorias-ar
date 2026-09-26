# Diccionario y metodología

## Grano y cobertura

Una fila de `fct_education_rates` representa **año base × territorio × nivel × grado publicado × indicador**. Hay 13 períodos, 27 territorios, 15 columnas por territorio y 3 indicadores: 15.795 filas. Se conserva el total de cada nivel además de los grados; no sumarlos entre sí.

`grade=0` significa total de nivel. Los grados 1–12 representan años de escolaridad conforme al encabezado original, no necesariamente el año ordinal dentro del secundario. La estructura 6–6 ubica el inicio secundario en el año 7; la estructura 7–5 lo ubica en el 8. No asumir que un grado 7 pertenece siempre al mismo nivel.

Los códigos provinciales se mantienen como texto con ceros iniciales. `00`, `06C` y `06R` son convenciones del proyecto para total nacional, Conurbano y resto de Buenos Aires. Conurbano y resto no son provincias adicionales: son ámbitos contenidos en Buenos Aires.

## Campos principales

| Campo | Tipo | Significado |
|---|---|---|
| observation_id | texto | Clave determinista de la observación |
| year_from / year_to | entero | Inicio/fin de transición entre ciclos lectivos |
| geo_code / geo_name | texto | Identificador y nombre normalizado del ámbito |
| geo_type | texto | pais, provincia o subprovincia |
| parent_code | texto/nulo | 06 para las subdivisiones bonaerenses |
| structure | texto | 6-6, 7-5 o mixta (nacional) |
| level | texto | primaria o secundaria |
| grade | entero | 0 = total; otros = año de escolaridad publicado |
| indicator | texto | abandono, promocion o repitencia |
| rate_pct | decimal/nulo | Tasa en escala porcentual: 7.28 significa 7,28 %, no 0,0728 |
| value_status | texto | observado, fuera_rango_teorico, no_aplica o faltante |
| pandemic_context | 0/1 | Regla del proyecto para años base 2019, 2020 y 2021 |
| methodology_break | 0/1 | Secundaria 2024, Buenos Aires, sus subdivisiones y total país |
| source_sha256 | texto | Hash del ZIP exacto |
| source_url/member/sheet/cell | texto | URL, archivo interno, hoja y celda originales |

## Indicadores y alineación temporal

La promoción efectiva mide el pasaje de alumnos al siguiente año de estudio; la repitencia registra reinscripción como repitientes; el abandono interanual refiere a quienes no se matriculan en el año lectivo siguiente, según el modelo de flujos del productor. Las hojas de promoción y repitencia usan el año base; las de abandono indican ambos años. El proyecto alinea `2024` con `2024-2025`, no con `2023-2024`.

No se recalculan tasas a partir de matrícula: este dataset no contiene los denominadores. Una brecha de 2 pp es la resta entre dos tasas, no un aumento relativo de 2 %.

## Reglas de calidad

- La cobertura debe incluir los 27 ámbitos en cada hoja, y los años deben coincidir entre indicadores.
- Un texto inesperado en una celda numérica bloquea la carga.
- Un nulo de un grado no aplicable por estructura se distingue de un faltante.
- Se mantiene todo valor numérico finito, incluso fuera de 0–100. La hoja oficial «Limitaciones» explica que los movimientos entre cohortes o sistemas pueden sesgar las tasas de flujo.
- Los totales deben satisfacer promoción + repitencia + abandono ≈ 100 con tolerancia de 0,15 pp. Es un control de consistencia, no una corrección de los datos.
- Se validan unicidad, relaciones con dimensiones y 24 provincias por nivel y período.

Snapshot inicial: 13.739 celdas observadas dentro de rango, 1.042 fuera del rango teórico y 1.014 no aplicables. No hay faltantes no estructurales en este snapshot. No interpretar los 1.042 valores como alumnos ni como errores confirmados.

## Comparabilidad y señal exploratoria

`raw_change_pp` conserva la diferencia publicada. `comparable_change_pp` sólo aparece si hay año anterior consecutivo, misma estructura, tasas presentes, sin marcas de rango, sin contexto de pandemia en ambos períodos y sin cambio metodológico en ambos períodos. Es una **regla de elegibilidad definida por el proyecto**, no una certificación de comparabilidad total.

`review_signal` indica `revisar_aumento` si el cambio elegible es ≥ 2 pp; `sin_senal_por_umbral` en caso contrario; `requiere_contexto` si no es elegible. El umbral es exploratorio y no oficial. La ausencia de señal no demuestra ausencia de problemas educativos.

La nota del Excel 2024 explica el cambio de definición operativa de secundaria de Buenos Aires. Se suprime su variación comparable y la del total nacional. Las brechas transversales se mantienen como descriptivas: la composición etaria y las estructuras distintas limitan las comparaciones entre provincias. Otras reformas no codificadas pueden existir; ampliar las reglas requiere revisar notas de fuente.
