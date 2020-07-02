import datetime
import logging
import sys

import click
import yaml
from clarityPublisherJob import DATE_FORMAT
from clarityPublisherJob.biquery import BigQueryClient
from clarityPublisherJob.clients.delta import DeltaDirectClient
from clarityPublisherJob.config.app import ApplicationConfig


def query_printer(name, query):
    delimiter = "-" * 20
    print(delimiter)
    print("-- START QUERY {}".format(name.upper()))
    print(delimiter)

    print(query)

    print(delimiter)
    print("-- END QUERY {}".format(name.upper()))
    print(delimiter)


@click.command()
@click.argument('execution_date', type=click.STRING)
@click.argument('transfer_name', type=click.STRING)
@click.argument('config_location')
def query_debug(execution_date, transfer_name, config_location):
    """
        This will print the query used in the pipeline

        \b
        EXECUTION_DATE: date of pipeline execution YYYYMMDD
        TRANSFER_NAME: pipeline name to transfer
        CONFIG_LOCATION: local /path/to/config/file

        """
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler(sys.stdout))

    configuration = yaml.load(open(config_location))
    app_config = ApplicationConfig(configuration, logger)

    transfer = app_config.get_transfer(transfer_name)
    execution_date = datetime.datetime.strptime(execution_date, DATE_FORMAT)
    last_day_with_full_data = execution_date - datetime.timedelta(days=1)

    if transfer.is_truncate:
        print("no query used")
        return

    params = {
        "bq_client": BigQueryClient(project=transfer.project),
        "transfer": transfer,
        "execution_date": execution_date,
        "logger": logger
    }

    delta = DeltaDirectClient(**params)
    query_printer('direct', delta.build_tmp_query())
