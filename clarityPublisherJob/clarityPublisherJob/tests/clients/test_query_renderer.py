import os

import yaml
from jinja2 import Environment, PackageLoader
from sidPublisherJob.clients.query_renderer import QueryRenderer
from sidPublisherJob.config.app import ApplicationConfig

from tests import RESOURCE_DIR
from tmg_etl_library.cloud_logger.cloud_logger import Logger

PACKAGE_LOADER = PackageLoader('sidPublisherJob', 'queries')


def _read_query(file_name):
    with open(os.path.join(RESOURCE_DIR, file_name)) as query_file:
        return query_file.read().strip()


def _get_app_config(mocker):
    config_content = yaml.load(
        open(os.path.join(RESOURCE_DIR, 'test_config.yml'))
    )
    mocker.patch('tmg_etl_library.cloud_logger.cloud_logger.Logger')
    logger = Logger('test-app', __name__, google_project_id='google-project-id')

    return ApplicationConfig(config_content, logger)


def test_delta_direct(mocker):
    app_config = _get_app_config(mocker)

    renderer = QueryRenderer(
        Environment(loader=PACKAGE_LOADER),
        app_config.get_transfer('fact_interaction')
    )

    query = renderer.delta_direct_query(
        '2019-01-01',
        [
            'sk_interaction',
            'bk_source_driver',
            'bk_agent',
            'fk_date_created',
            'fk_time_created',
            'fk_date_closed',
            'fk_time_closed',
            'fk_interaction_detail',
            'fk_interaction_detail_linked_case',
            'fk_interaction_text',
            'fk_account',
            'fk_retailer',
            'fk_source_subscription',
            'fk_subscription_type',
            'fk_product',
            'fk_agent',
            'fk_agent_lmd',
            'fk_date_next_call_due',
            'fk_date_stage_1_call',
            'fk_date_stage_2_call',
            'fk_date_stage_3_call',
            'fk_date_stage_4_call',
            'fk_time_stage_1_call',
            'fk_time_stage_2_call',
            'fk_time_stage_3_call',
            'fk_time_stage_4_call',
            'fk_date_of_issue',
            'last_modified_datetime',
            'flag_closed',
            'flag_deleted',
            'flag_scheduled_callback_in_past',
            'value',
            'interaction_initial_response_seconds',
            'interaction_duration_seconds',
            'chat_agent_response_time_average_seconds',
            'chat_agent_response_time_max_seconds',
            'chat_agent_message_count',
            'chat_visitor_response_time_average_seconds',
            'chat_visitor_response_time_max_seconds',
            'chat_visitor_response_time_abandoned_seconds',
            'chat_visitor_message_count',
            'flag_sla_met',
            'performance_band',
            'count_interactions',
            'dm_created_datetime',
            'dm_updated_datetime',
            'fk_date_outcome_changed',
            'fk_time_outcome_changed'
        ]
    )

    assert query.strip() == _read_query('query_delta_direct.sql')

    renderer = QueryRenderer(
        Environment(loader=PACKAGE_LOADER),
        app_config.get_transfer('fact_subscription_event')
    )

    query = renderer.delta_direct_query(
        '2019-01-01',
        [
            'sk_subscription_event',
            'fk_event_type',
            'fk_date_created',
            'fk_account',
            'fk_campaign',
            'fk_incentive',
            'fk_extra',
            'fk_account_secondary',
            'fk_promo_code',
            'fk_agent',
            'fk_date_term_start',
            'fk_date_term_end',
            'fk_date_trial_end',
            'fk_date_effective',
            'fk_source_subscription_effective',
            'fk_product_effective',
            'fk_subscription_type_effective',
            'fk_retailer_effective',
            'fk_plan_effective',
            'fk_source_subscription_existing',
            'fk_product_existing',
            'fk_subscription_type_existing',
            'fk_retailer_existing',
            'fk_plan_existing',
            'fk_event_driver',
            'bk_source_driver',
            'bk_agent',
            'created_datetime',
            'method',
            'value',
            'net_value',
            'tax_value',
            'type',
            'status',
            'voucher_weeks',
            'reason',
            'sub_reason',
            'offer_code',
            'redemption_code',
            'count_days_to_term_end',
            'count_gap_days',
            'flag_current_chain',
            'flag_during_trial',
            'count_events',
            'dm_created_datetime',
            'dm_updated_datetime',
            'indexhash'
        ]
    )

    assert query.strip() == _read_query('query_delta_direct_custom_MRI.sql')


def test_load_data_infile(mocker):
    app_config = _get_app_config(mocker)

    renderer = QueryRenderer(
        Environment(loader=PACKAGE_LOADER),
        app_config.get_transfer('fact_interaction')
    )

    query = renderer.load_data_infile(
        '/path/to/local/file',
        'test_schema',
        'test_table',
        [
            'id',
            'firstname',
            'lastname',
            'address',
            'date_of_birth'
        ]
    )

    assert query.strip() == _read_query('query_load_data_infile.sql')
