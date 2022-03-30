import traceback
from datetime import datetime

import yaml
from google.cloud import storage
from clarityPublisherJob import DATE_FORMAT
from clarityPublisherJob.biquery import BigQueryClient
from clarityPublisherJob.clients.delta import DeltaDirectClient
from clarityPublisherJob.clients.truncate import TruncateClient
from clarityPublisherJob.config.app import ApplicationConfig
from clarityPublisherJob.sanity_check import SanityCheck
from clarityPublisherJob.tmg_etl import TMGETL
from tmg_etl_library.cloud_logger.cloud_logger import Logger

APP_NAME = 'clarityPublisherJob'
INSTANCE_NAME_FORMAT = 'clarityPublisherJob{date}'

PYTHON_MIN_VERSION = (3, 6)


class ETL(TMGETL):

    def __init__(self, execution_date, transfer_name, config_location, full_refresh=False):
        """

        :param execution_date:
        :param transfer_name:
        :param config_location:
        :param delta_start_date:
        :param full_refresh:
        """
        # added this as parent now contains __init__()
        super().__init__()

        self._config_location = config_location
        self._transfer_name = transfer_name
        self._execution_date = execution_date
        self._full_refresh = full_refresh

        application_configuration = self.download_config(self._config_location)
        project_id = application_configuration['project']

        self._logger = Logger(APP_NAME, __name__, google_project_id=project_id)
        self.app_config = ApplicationConfig(
            application_configuration, self._logger)

        self._logger.push_to_pubsub = self.app_config.push_logger_to_pubsub

    @property
    def logger(self):
        """
        Get the logger
        :return: logger
        """
        return self._logger

    @property
    def execution_date(self):
        return datetime.strptime(self._execution_date, DATE_FORMAT)

    def pipeline(self):

        transfer_name = self._transfer_name
        transfer = self.app_config.get_transfer(transfer_name)

        bq_client = BigQueryClient(project=transfer.project)

        if transfer.is_truncate or self._full_refresh:
            data_transfer_client = TruncateClient(
                bq_client,
                transfer,
                self.execution_date,
                self.logger
            )
        else:
            data_transfer_client = DeltaDirectClient(
                bq_client, transfer, self.execution_date, self.logger
            )

        try:
            data_transfer_client.run()
            self._do_sanity_check(transfer)

        except Exception:
            error = traceback.format_exc()
            self.logger.info(error)
            raise RuntimeError(error)

    def _do_sanity_check(self, transfer):
        """
        Check the difference of number of rows between the source and the destination table
        :param transfer_name:
        :return:
        """

        sanity_check = SanityCheck(self.logger, transfer)

        discrepancy = sanity_check.run()
        self.logger.info(f'Sanity Check Difference: {discrepancy}')

        absolute_discrepancy = abs(discrepancy)
        if absolute_discrepancy > 1:
            raise RuntimeError(
                f'Data is available, but tables rows count are not matching: mysql - bigquery: {discrepancy}')

    def download_config(self, config_location):
        config_location = config_location.rstrip()
        if 'gs' == config_location[:2]:
            try:
                bucket, file = config_location.replace('gs://', '').split('/')
            except ValueError:
                raise RuntimeError(
                    'Config Location must be of form "bucket/file"')
            storage_client = storage.Client()
            bucket = storage_client.get_bucket(bucket)
            file = bucket.blob(file)
            file_content = file.download_as_string()
        else:
            with open(config_location, 'r') as file:
                file_content = file.read()

        return yaml.load(file_content)
