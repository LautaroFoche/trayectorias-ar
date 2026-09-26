select *, value - 1.96 * standard_error as ci95_low,
value + 1.96 * standard_error as ci95_high,
case when standard_error is null then 'No disponible' else 'Aproximación normal: estimación ± 1,96 EE' end as interval_method
from {{ ref('fct_context_indicators') }} where source_id <> 'wdi_data'
