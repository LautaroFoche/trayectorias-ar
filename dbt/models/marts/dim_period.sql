select distinct year_from, year_to,
 cast(year_from as {{ dbt.type_string() }}) || '–' || cast(year_to as {{ dbt.type_string() }}) as transition_label
from {{ ref('stg_observations') }}
