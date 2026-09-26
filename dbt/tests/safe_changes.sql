select * from {{ ref('mart_continuity') }}
where (comparable_yoy=0 and comparable_change_pp is not null)
 or (methodology_break=1 and comparable_yoy=1)
 or (pandemic_context=1 and comparable_yoy=1)
