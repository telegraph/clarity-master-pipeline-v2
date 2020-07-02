-- delta_direct.sql
WITH LAST_VALUES AS (
    SELECT
        sk_interaction,
        MAX(RAW_TABLE.PARTITION_FIELD_DATE) AS MOST_RECENT
    FROM `tmg-plat-dev.sid_development.raw_fact_interaction` RAW_TABLE
    WHERE
        1=1
        AND RAW_TABLE.PARTITION_FIELD_DATE >= date(TIMESTAMP('2019-01-01'))
    GROUP BY sk_interaction
)
SELECT
    RAW_TABLE.sk_interaction as sk_interaction,
    RAW_TABLE.bk_source_driver as bk_source_driver,
    RAW_TABLE.bk_agent as bk_agent,
    RAW_TABLE.fk_date_created as fk_date_created,
    RAW_TABLE.fk_time_created as fk_time_created,
    RAW_TABLE.fk_date_closed as fk_date_closed,
    RAW_TABLE.fk_time_closed as fk_time_closed,
    RAW_TABLE.fk_interaction_detail as fk_interaction_detail,
    RAW_TABLE.fk_interaction_detail_linked_case as fk_interaction_detail_linked_case,
    RAW_TABLE.fk_interaction_text as fk_interaction_text,
    RAW_TABLE.fk_account as fk_account,
    RAW_TABLE.fk_retailer as fk_retailer,
    RAW_TABLE.fk_source_subscription as fk_source_subscription,
    RAW_TABLE.fk_subscription_type as fk_subscription_type,
    RAW_TABLE.fk_product as fk_product,
    RAW_TABLE.fk_agent as fk_agent,
    RAW_TABLE.fk_agent_lmd as fk_agent_lmd,
    RAW_TABLE.fk_date_next_call_due as fk_date_next_call_due,
    RAW_TABLE.fk_date_stage_1_call as fk_date_stage_1_call,
    RAW_TABLE.fk_date_stage_2_call as fk_date_stage_2_call,
    RAW_TABLE.fk_date_stage_3_call as fk_date_stage_3_call,
    RAW_TABLE.fk_date_stage_4_call as fk_date_stage_4_call,
    RAW_TABLE.fk_time_stage_1_call as fk_time_stage_1_call,
    RAW_TABLE.fk_time_stage_2_call as fk_time_stage_2_call,
    RAW_TABLE.fk_time_stage_3_call as fk_time_stage_3_call,
    RAW_TABLE.fk_time_stage_4_call as fk_time_stage_4_call,
    RAW_TABLE.fk_date_of_issue as fk_date_of_issue,
    RAW_TABLE.last_modified_datetime as last_modified_datetime,
    RAW_TABLE.flag_closed as flag_closed,
    RAW_TABLE.flag_deleted as flag_deleted,
    RAW_TABLE.flag_scheduled_callback_in_past as flag_scheduled_callback_in_past,
    RAW_TABLE.value as value,
    RAW_TABLE.interaction_initial_response_seconds as interaction_initial_response_seconds,
    RAW_TABLE.interaction_duration_seconds as interaction_duration_seconds,
    RAW_TABLE.chat_agent_response_time_average_seconds as chat_agent_response_time_average_seconds,
    RAW_TABLE.chat_agent_response_time_max_seconds as chat_agent_response_time_max_seconds,
    RAW_TABLE.chat_agent_message_count as chat_agent_message_count,
    RAW_TABLE.chat_visitor_response_time_average_seconds as chat_visitor_response_time_average_seconds,
    RAW_TABLE.chat_visitor_response_time_max_seconds as chat_visitor_response_time_max_seconds,
    RAW_TABLE.chat_visitor_response_time_abandoned_seconds as chat_visitor_response_time_abandoned_seconds,
    RAW_TABLE.chat_visitor_message_count as chat_visitor_message_count,
    RAW_TABLE.flag_sla_met as flag_sla_met,
    RAW_TABLE.performance_band as performance_band,
    RAW_TABLE.count_interactions as count_interactions,
    RAW_TABLE.dm_created_datetime as dm_created_datetime,
    RAW_TABLE.dm_updated_datetime as dm_updated_datetime,
    RAW_TABLE.fk_date_outcome_changed as fk_date_outcome_changed,
    RAW_TABLE.fk_time_outcome_changed as fk_time_outcome_changed
FROM `tmg-plat-dev.sid_development.raw_fact_interaction` RAW_TABLE
INNER JOIN LAST_VALUES
ON RAW_TABLE.sk_interaction = LAST_VALUES.sk_interaction
AND RAW_TABLE.PARTITION_FIELD_DATE = LAST_VALUES.MOST_RECENT
