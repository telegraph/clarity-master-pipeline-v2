LOAD DATA LOCAL infile '{{ data_file_path }}'
REPLACE
INTO TABLE {{ table_schema}}.{{table_name}}
CHARACTER SET 'utf8mb4'
FIELDS TERMINATED BY '\t'
	ESCAPED BY '\"'
IGNORE 1 LINES
(
{%- for field in field_list -%}
    @{{field}}
    {%- if not loop.last -%}, {% endif -%}
{% endfor -%}
)
SET
{%- for field in field_list %}
`{{ field }}` = nullif(@{{field}}, '')
{%- if not loop.last -%},{%- endif -%}
{% endfor %}
;

