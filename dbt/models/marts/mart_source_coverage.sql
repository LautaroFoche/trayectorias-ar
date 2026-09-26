with counts as (
select source_id, year, value from {{ ref('fct_context_indicators') }}
union all
select 'educacion_' || indicator, year_from, rate_pct from {{ ref('fct_education_rates') }}
)
select s.*, count(c.source_id) as observations, count(c.value) as observed,
count(c.source_id)-count(c.value) as missing_or_not_applicable,
min(c.year) as first_year, max(c.year) as last_year,
case when s.source_id like 'wdi_meta_%' then 'metadatos' else 'datos' end as artifact_role
from {{ source('education', 'source_catalog') }} s left join counts c on s.source_id=c.source_id
group by s.source_id,s.family,s.producer,s.url,s.sha256,s.path,s.retrieved_at,s.format,s.bytes
