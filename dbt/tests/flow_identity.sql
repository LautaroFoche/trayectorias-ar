-- Desviación tolerada: 0,15 pp por redondeo de tres tasas. No se recortan valores.
select * from {{ ref('mart_continuity') }}
where abandonment_pct is null or promotion_pct is null or repetition_pct is null
 or abs(flow_residual_pp)>0.15
