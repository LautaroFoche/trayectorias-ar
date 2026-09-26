-- El total nacional proviene de la fuente: nunca es el promedio de provincias.
with totals as (
 select year_from, year_to, geo_code, geo_name, geo_type, structure, level,
 max(case when indicator='abandono' then rate_pct end) as abandonment_pct,
 max(case when indicator='promocion' then rate_pct end) as promotion_pct,
 max(case when indicator='repitencia' then rate_pct end) as repetition_pct,
 max(pandemic_context) as pandemic_context,
 max(methodology_break) as methodology_break,
 max(outside_theoretical_range) as outside_theoretical_range
 from {{ ref('int_transitions') }} where grade=0
 group by year_from, year_to, geo_code, geo_name, geo_type, structure, level
), previous as (
 select *,
 lag(year_from) over(partition by geo_code,level order by year_from) as previous_year,
 lag(abandonment_pct) over(partition by geo_code,level order by year_from) as previous_abandonment,
 lag(structure) over(partition by geo_code,level order by year_from) as previous_structure,
 lag(pandemic_context) over(partition by geo_code,level order by year_from) as previous_pandemic,
 lag(methodology_break) over(partition by geo_code,level order by year_from) as previous_break,
 lag(outside_theoretical_range) over(partition by geo_code,level order by year_from) as previous_outside_range
 from totals
), deltas as (
 select p.*, n.abandonment_pct as national_abandonment_pct,
 p.abandonment_pct-n.abandonment_pct as gap_vs_nation_pp,
 p.abandonment_pct-p.previous_abandonment as raw_change_pp,
 case when p.previous_year=p.year_from-1 and p.structure=p.previous_structure
 and p.pandemic_context=0 and p.previous_pandemic=0
 and p.methodology_break=0 and p.previous_break=0
 and p.outside_theoretical_range=0 and p.previous_outside_range=0
 and p.abandonment_pct is not null and p.previous_abandonment is not null
 then 1 else 0 end as comparable_yoy,
 p.promotion_pct+p.repetition_pct+p.abandonment_pct-100 as flow_residual_pp
 from previous p left join totals n
 on n.year_from=p.year_from and n.level=p.level and n.geo_code='00'
)
select *,
 case when comparable_yoy=1 then raw_change_pp end as comparable_change_pp,
 case when comparable_yoy=0 then 'requiere_contexto'
 when raw_change_pp >= {{ var('attention_threshold_pp') }} then 'revisar_aumento'
 else 'sin_senal_por_umbral' end as review_signal
from deltas
