select * from {{ ref('fct_education_rates') }}
where (rate_pct is null and value_status not in ('no_aplica','faltante'))
 or (rate_pct is not null and value_status in ('no_aplica','faltante'))
 or (rate_pct is not null and (rate_pct<0 or rate_pct>100) and outside_theoretical_range<>1)
