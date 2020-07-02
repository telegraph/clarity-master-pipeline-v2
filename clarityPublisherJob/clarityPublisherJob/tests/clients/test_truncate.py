import os

import yaml

from sidPublisherJob.clients.blob import BlobComposer
from sidPublisherJob.clients.truncate import TruncateClient
from sidPublisherJob.config.app import ApplicationConfig

from tests import RESOURCE_DIR
from tmg_etl_library.cloud_logger.cloud_logger import Logger


def test_truncate_client_build_drop_indexes_list(mocker):
    config_content = yaml.load(
        open(os.path.join(RESOURCE_DIR, 'test_config.yml'))
    )

    mocker.patch('tmg_etl_library.cloud_logger.cloud_logger.Logger')
    logger = Logger('test-app', __name__, google_project_id='google-project-id')

    app_config = ApplicationConfig(config_content, logger)

    create_indexes = TruncateClient.build_create_index_list(app_config.get_transfer('dim_product'))

    key_name = ('dim_product_name', 'name')
    key_nk = ('dim_product_nk', 'source_id,source_id_2,name')
    assert set(create_indexes.keys()) == {key_name, key_nk}

    assert create_indexes[key_name] == 'CREATE INDEX dim_product_name ON sid.dim_product (name);'
    assert create_indexes[key_nk] == 'CREATE INDEX dim_product_nk ON sid.dim_product (source_id,source_id_2,name);'


def test_blob_manager_chunk_single():
    single_source_csv = [f'my_file_0']
    blob_manager = BlobComposer('my_file', single_source_csv)
    assert blob_manager.full_file_name == 'my_file_full.csv'

    assert list(blob_manager.chunks) == [single_source_csv]


def test_blob_manager_chunk_small():
    small_source_csv = [f'my_file_{i}' for i in range(0, 10)]

    blob_manager = BlobComposer('my_file', small_source_csv)
    assert list(blob_manager.chunks) == [small_source_csv]


def test_blob_manager_chunk_big():
    big_source_csv = [f'my_file_{i}' for i in range(0, 33)]
    blob_manager = BlobComposer('my_file', big_source_csv)

    assert list(blob_manager.chunks) == [
        [f'my_file_{i}' for i in range(0, 32)],
        ['my_file_32']
    ]


def test_blob_manager_chunk_huge():
    huge_source_csv = [f'my_file_{i}' for i in range(0, 65)]
    blob_manager = BlobComposer('my_file', huge_source_csv)

    assert list(blob_manager.chunks) == [
        [f'my_file_{i}' for i in range(0, 32)],
        [f'my_file_{i}' for i in range(32, 64)],
        [f'my_file_64']
    ]


def test_blob_manager_get_intermediary_mapping_smaller_than_max():
    small_source_csv = [f'my_file_{i}' for i in range(0, 10)]

    blob_manager = BlobComposer('my_file', small_source_csv)

    assert blob_manager.intermediary_mapping == []


def test_blob_manager_get_intermediary_mapping_over():
    small_source_csv = [f'my_file_{i}' for i in range(0, 33)]

    blob_manager = BlobComposer('my_file', small_source_csv)

    assert blob_manager.intermediary_mapping == [
        ('my_file_intermediary_0.csv', [f'my_file_{i}' for i in range(0, 32)]),
        ('my_file_intermediary_1.csv', ['my_file_32'])
    ]
