import os
from datetime import datetime

import yaml
from sidPublisherJob.config.app import ApplicationConfig
from sidPublisherJob.config.transfer import (
    TransferConfiguration,
    TransferMysqlConfiguration,
    TransferBigQueryConfiguration,
    TransferGSConfiguration
)
from tests import RESOURCE_DIR
from tmg_etl_library.cloud_logger.cloud_logger import Logger


def test_app_configuration(mocker):
    config_content = yaml.load(
        open(os.path.join(RESOURCE_DIR, 'test_config.yml'))
    )

    mocker.patch('tmg_etl_library.cloud_logger.cloud_logger.Logger')
    logger = Logger('test-app', __name__, google_project_id='google-project-id')

    app_config = ApplicationConfig(config_content, logger)
    assert app_config.project == 'tmg-plat-dev'
    assert app_config.push_logger_to_pubsub == False


def test_transfer_configuration():

    transfer_name = 'dim_product'
    transfer = _build_transfer_object(transfer_name)

    assert transfer.name == transfer_name
    assert isinstance(transfer.mysql, TransferMysqlConfiguration)
    assert isinstance(transfer.bigquery, TransferBigQueryConfiguration)
    assert isinstance(transfer.gcs, TransferGSConfiguration)

    assert transfer.mysql.destination_table == 'sid.dim_product'

    assert transfer.bigquery.bq_full_table_name == 'tmg-plat-dev.sid_development.dim_product'

    assert transfer.gcs.extract_file_uri(datetime(2019, 1, 1)) == 'gs://nick_sid/dim_product_20190101'


def test_transfer_delta():

    transfer_name = 'fact_interaction'
    transfer = _build_transfer_object(transfer_name)
    assert transfer.delta.fields_to_omit == ['PARTITION_FIELD_DATE']

    transfer_name = 'fact_subscription_event'

    transfer = _build_transfer_object(transfer_name)

    assert transfer.delta.fields_to_omit == [ 'PARTITION_FIELD_DATE', 'OPERATION', 'PIPELINE_ORDER', 'PIPELINE_NAME', 'source' ]
    assert transfer.delta.most_recent_identifier == "CAST(CONCAT(FORMAT_DATE('%Y%m%d', RAW_TABLE.PARTITION_FIELD_DATE), CAST(RAW_TABLE.PIPELINE_ORDER AS STRING)) AS INT64)"


def test_transfer_truncate():

    transfer_name = 'dim_product'
    transfer = _build_transfer_object(transfer_name)


def _build_transfer_object(transfer_name):

    config_content = yaml.load(
        open(os.path.join(RESOURCE_DIR, 'test_config.yml'))
    )

    mysql_config = config_content['mysql']
    bq_config = config_content['bq']
    gcs_config = config_content['gcs']
    transfer_configuration = config_content['transfers'][transfer_name]

    return TransferConfiguration(
        config_content['project'],
        transfer_name,
        transfer_configuration,
        mysql_config,
        bq_config,
        gcs_config
    )



