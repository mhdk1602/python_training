{% macro test_expression_is_greater_than_zero(model, column_name) %}
  select count(*)
  from {{ model }}
  where "{{ column_name }}" <= 0
{% endmacro %}