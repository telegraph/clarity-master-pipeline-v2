-- delta_direct.sql
WITH LAST_VALUES AS (
    SELECT
        sk_subscription_event,
        MAX(CAST(CONCAT(FORMAT_DATE('%Y%m%d', RAW_TABLE.PARTITION_FIELD_DATE), CAST(RAW_TABLE.PIPELINE_ORDER AS STRING)) AS INT64)) AS MOST_RECENT
    FROM `tmg-plat-dev.sid_development.raw_fact_subscription_event` RAW_TABLE
    WHERE
        1=1
        AND RAW_TABLE.PARTITION_FIELD_DATE >= date(TIMESTAMP('2019-01-01'))
    GROUP BY sk_subscription_event
)
SELECT
    RAW_TABLE.sk_subscription_event as sk_subscription_event,
    RAW_TABLE.fk_event_type as fk_event_type,
    RAW_TABLE.fk_date_created as fk_date_created,
    RAW_TABLE.fk_account as fk_account,
    RAW_TABLE.fk_campaign as fk_campaign,
    RAW_TABLE.fk_incentive as fk_incentive,
    RAW_TABLE.fk_extra as fk_extra,
    RAW_TABLE.fk_account_secondary as fk_account_secondary,
    RAW_TABLE.fk_promo_code as fk_promo_code,
    RAW_TABLE.fk_agent as fk_agent,
    RAW_TABLE.fk_date_term_start as fk_date_term_start,
    RAW_TABLE.fk_date_term_end as fk_date_term_end,
    RAW_TABLE.fk_date_trial_end as fk_date_trial_end,
    RAW_TABLE.fk_date_effective as fk_date_effective,
    RAW_TABLE.fk_source_subscription_effective as fk_source_subscription_effective,
    RAW_TABLE.fk_product_effective as fk_product_effective,
    RAW_TABLE.fk_subscription_type_effective as fk_subscription_type_effective,
    RAW_TABLE.fk_retailer_effective as fk_retailer_effective,
    RAW_TABLE.fk_plan_effective as fk_plan_effective,
    RAW_TABLE.fk_source_subscription_existing as fk_source_subscription_existing,
    RAW_TABLE.fk_product_existing as fk_product_existing,
    RAW_TABLE.fk_subscription_type_existing as fk_subscription_type_existing,
    RAW_TABLE.fk_retailer_existing as fk_retailer_existing,
    RAW_TABLE.fk_plan_existing as fk_plan_existing,
    RAW_TABLE.fk_event_driver as fk_event_driver,
    RAW_TABLE.bk_source_driver as bk_source_driver,
    RAW_TABLE.bk_agent as bk_agent,
    RAW_TABLE.created_datetime as created_datetime,
    RAW_TABLE.method as method,
    RAW_TABLE.value as value,
    RAW_TABLE.net_value as net_value,
    RAW_TABLE.tax_value as tax_value,
    RAW_TABLE.type as type,
    RAW_TABLE.status as status,
    RAW_TABLE.voucher_weeks as voucher_weeks,
    RAW_TABLE.reason as reason,
    RAW_TABLE.sub_reason as sub_reason,
    RAW_TABLE.offer_code as offer_code,
    RAW_TABLE.redemption_code as redemption_code,
    RAW_TABLE.count_days_to_term_end as count_days_to_term_end,
    RAW_TABLE.count_gap_days as count_gap_days,
    RAW_TABLE.flag_current_chain as flag_current_chain,
    RAW_TABLE.flag_during_trial as flag_during_trial,
    RAW_TABLE.count_events as count_events,
    RAW_TABLE.dm_created_datetime as dm_created_datetime,
    RAW_TABLE.dm_updated_datetime as dm_updated_datetime,
    RAW_TABLE.indexhash as indexhash
FROM `tmg-plat-dev.sid_development.raw_fact_subscription_event` RAW_TABLE
INNER JOIN LAST_VALUES
ON RAW_TABLE.sk_subscription_event = LAST_VALUES.sk_subscription_event
AND CAST(CONCAT(FORMAT_DATE('%Y%m%d', RAW_TABLE.PARTITION_FIELD_DATE), CAST(RAW_TABLE.PIPELINE_ORDER AS STRING)) AS INT64) = LAST_VALUES.MOST_RECENT
