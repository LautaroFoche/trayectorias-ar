select * from {{ ref('fct_context_indicators') }} where source_id = 'wdi_data'
