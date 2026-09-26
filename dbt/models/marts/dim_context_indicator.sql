select distinct source_id, indicator, indicator_label, unit, population, evidence_kind from {{ ref('fct_context_indicators') }}
