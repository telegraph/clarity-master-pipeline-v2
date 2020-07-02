import sys

import click
from clarityPublisherJob.etl import PYTHON_MIN_VERSION, ETL

assert tuple(sys.version_info) >= PYTHON_MIN_VERSION, "Please update to Python {}.{}".format(
    PYTHON_MIN_VERSION[0], PYTHON_MIN_VERSION[0])


@click.command()
@click.argument('execution_date', type=click.STRING)
@click.argument('transfer_name', type=click.STRING)
@click.argument('config_location')
@click.option('--full-refresh', is_flag=True)
def run(execution_date, transfer_name, config_location, full_refresh):
    """
    This will run the pipeline

    \b
    EXECUTION_DATE: date of pipeline execution YYYYMMDD
    TRANSFER_NAME: pipeline name to transfer
    CONFIG_LOCATION: location of config file in form gs://bucket/filename or /path/to/file

    \b
    --full-refresh: full refresh the table (bypass transfer method)

    """
    etl = ETL(
        execution_date,
        transfer_name,
        config_location,
        full_refresh
    )

    etl.execute()


# this is for debuggin in pycharm #
# if __name__ == "__main__":
 #   import sys

  #  run(sys.argv[1:])
