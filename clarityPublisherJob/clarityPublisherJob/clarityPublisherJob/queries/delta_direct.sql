-- delta_direct.sql
WITH LAST_VALUES AS (
    SELECT
        {{ table_key }},
        MAX({{ most_recent_identifier }}) AS MOST_RECENT
    FROM `{{ raw_table }}` RAW_TABLE
    WHERE
        1=1
        AND RAW_TABLE.PARTITION_FIELD_DATE >= date(TIMESTAMP('{{ date }}'))
    GROUP BY {{ table_key }}
)
SELECT
    {%- for col in columns_to_select %}
    RAW_TABLE.{{col }} as {{ col }}{{ "," if not loop.last }}
    {%- endfor %}
FROM `{{ raw_table }}` RAW_TABLE
INNER JOIN LAST_VALUES
ON RAW_TABLE.{{ table_key }} = LAST_VALUES.{{ table_key }}
AND {{ most_recent_identifier }} = LAST_VALUES.MOST_RECENT

