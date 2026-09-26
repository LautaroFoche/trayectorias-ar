select observation_id, year_from, geo_code, level, grade, structure, indicator,
 rate_pct, value_status, pandemic_context, methodology_break, outside_theoretical_range,
 source_sha256, source_url, source_member, source_sheet, source_cell
from {{ ref('int_transitions') }}
