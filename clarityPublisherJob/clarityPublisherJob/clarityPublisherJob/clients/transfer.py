import os
import time
import uuid
from collections import OrderedDict
from datetime import datetime

import pandas as pd
import mysql.connector
from google.cloud import bigquery
from jinja2 import Environment, PackageLoader
from clarityPublisherJob.biquery import BigQueryClient
from clarityPublisherJob.clients.query_renderer import QueryRenderer
from clarityPublisherJob.traffic_light import TrafficLight


class TransferClient(object):

    def __init__(self, bq_client, transfer, execution_date, logger):
        """
        :param BigQueryClient bq_client:
        :param TransferConfiguration transfer:
        :param datetime.datetime execution_date:
        :param logger:
        """
        self.transfer = transfer
        self.id = uuid.uuid4()
        self.execution_date = execution_date
        self.logger = logger
        self.bq_client = bq_client

        self.jinja_env = Environment(
            loader=PackageLoader('clarityPublisherJob', 'queries')
        )

        self._query_renderer = QueryRenderer(
            Environment(
                loader=PackageLoader('clarityPublisherJob', 'queries')
            ),
            self.transfer
        )

        self.mysql_connection = mysql.connector.connect(
            host=self.transfer.mysql.host,
            user=self.transfer.mysql.user,
            passwd=self.transfer.mysql.password,
            database=self.transfer.mysql.schema
        )

        self.mysql_connection.autocommit = True

    def _mysql_connect_and_run_query(self, sql_connection, query):
        cursor = sql_connection.cursor()
        TrafficLight.block(self.logger)
        try:
            results = cursor.execute(query, multi=True)
            try:
                for result in results:
                    if result.with_rows:
                        self.logger.info("Rows produced by statement '{}':".format(
                            result.statement))
                        self.logger.info(result.fetchall())
                    else:
                        self.logger.info("Number of rows affected by statement '{}': {}".format(
                            result.statement, result.rowcount))
            except mysql.connector.Error as e:
                if e.errno == 1091:  # MySQL error - can not drop index check if exists
                    self.logger.warning(
                        'It is not possible to drop an index that does not exists')
                if e.errno == 1051 or e.errno == 1146:  # MySQL error - Table does not exist
                    self.logger.warning('Cant drop table which does not exist')

        except Exception as e:
            # TODO: Remove this??? At least make it more specific
            self.logger.error(
                'StopIteration Error - Dont know why. I think its a bug')
            # https://stackoverflow.com/questions/54987200/mysql-connector-cursor-execute-proceeds-silently-but-makes-no-changes-despite
            self.logger.error(repr(e))

        finally:
            TrafficLight.release(self.logger)

    def _mysql_table_exists(self, sql_connection, table):
        """
        :param sql_connection:
        :param table: schema.table
        :return: boolean
        """
        schema, table = table.split('.')
        cursor = sql_connection.cursor()
        TrafficLight.block(self.logger)
        query = '''
        SELECT count(*) FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_TYPE='BASE TABLE' 
        AND TABLE_NAME='{table}'
        AND TABLE_SCHEMA="{schema}"
        '''.format(
            table=table,
            schema=self.transfer.mysql.schema
        )

        try:
            cursor.execute(query)
            if cursor.fetchall()[0][0] < 1:
                return False
            return True

        except Exception as e:
            if 'StopIteration' in repr(e):
                return True
            else:
                return False

        finally:
            TrafficLight.release(self.logger)

    def _is_sql_replace_executing(self, response):
        """
        :param response: Response directly from MySQL
        :return:
        """
        executing = [process for process in response if 'executing' in process]
        info_field_index = 7
        replace_statements = [
            process for process in executing if 'replace' in process[info_field_index]]

        return bool(replace_statements)

    def _wait_for_mysql_free(self, sql_connection):
        """
        :param sql_connection:
        :return: None
        """
        cursor = sql_connection.cursor()
        TrafficLight.block(self.logger)
        query = 'show full processlist;'

        in_use = True

        while in_use:
            try:
                results = cursor.execute(query, multi=True)
                try:
                    for result in results:
                        if result.with_rows:
                            self.logger.info("Rows produced by statement '{}':".format(
                                result.statement))
                            response = result.fetchall()
                            self.logger.info(response)
                            executing = self._is_sql_replace_executing(
                                response)
                            if executing:
                                time.sleep(10)
                            else:
                                in_use = False
                except mysql.connector.Error as e:
                    self.logger.error('SQL Error')
                    self.logger.error(repr(e))
                    raise e

            except Exception as e:
                # TODO: Remove this??? At least make it more specific
                self.logger.error(
                    'StopIteration Error - Dont know why. I think its a bug')
                # https://stackoverflow.com/questions/54987200/mysql-connector-cursor-execute-proceeds-silently-but-makes-no-changes-despite
                self.logger.error(repr(e))
                in_use = False

        TrafficLight.release(self.logger)

    def _trunc_string(self, value):  # DT-4320
        '''
        static method used by pandas bq_to_csv to truncate string fields to > 250 bytes
        due to MySQL field limits

        Args: value - pandas row value - STRING 
        Returns: value STRING 
        '''

        try:
            if len(value) > 250:
                value = value[:250]
            return value
        except TypeError as e:
            return value

    def bq_to_gs(self, bq_table_name, gs_uri):
        """
        :param bq_table_name: table to extract in form project.dataset.table
        :param gs_uri: extract_file_uri to extract to
        :return:
        """

        # No need for Job ID - Files are overwritten as would be desired

        file_ending = self.transfer.gcs.file_ending

        table_ref = self.get_table_ref(bq_table_name)
        bytes = self.bq_client.get_table(table_ref).num_bytes

        if bytes > 10 ** 9:
            gs_uri = ['{}*{}'.format(gs_uri, file_ending)]
        else:
            gs_uri = ['{}{}'.format(gs_uri, file_ending)]

        self.logger.info(f'Extracting table {bq_table_name} to {gs_uri}')

        # Setting the file dimlimiter for csv files to tabs for clarity v2
        job_config = bigquery.job.ExtractJobConfig()
        job_config.field_delimiter = "\t"
        # Max GS object is 5TB. Need to check whether its better practice to split files
        extract_job = self.bq_client.extract_table(
            table_ref, gs_uri, job_config=job_config)  # API request
        result = extract_job.result()  # Waits for job to complete.

        if result.state != 'DONE' or result.errors:
            raise Exception('Failed extract job {} for table {}'.format(
                result.job_id, bq_table_name))

    def get_table_ref(self, full_table_name):
        """
        :param full_table_name: in form project.dataset.table
        :return: Google Table Reference
        """
        project, dataset, table = full_table_name.split('.')

        dataset_ref = self.bq_client.dataset(dataset, project)
        dataset = bigquery.Dataset(dataset_ref)
        table_ref = dataset.table(table)

        return table_ref

    def run_query(self, query, job_config, return_results=False):
        return self.bq_client.run_query(query, job_config, return_results)

    def mysql_get_table_schema(self, sql_connection, table):
        """
        Return schema information for a table in the form of
        {
        field: {
            type: "field_type",
            default: "default"
            },
            ...
        }
        :param sql_connection:
        :param table: schema.table
        :return: dict
        """
        schema, table = table.split('.')
        table_schema = []
        cursor = sql_connection.cursor()

        try:
            cursor.execute(f"SHOW columns from {schema}.{table}")
            table_schema = {column[0]: {
                "type": column[1], "default": column[4]} for column in cursor.fetchall()}

        except mysql.connector.Error as e:
            self.logger.error(f"Unable to read the schema for table {table}")
            self.logger.error(repr(e))
            raise e

        return OrderedDict(table_schema)

    def load_data_infile(self, full_file_blob, target_mysql_table):

        # download file locally
        database_name, table_name = target_mysql_table.split(".")
        time_string = int(datetime.now().timestamp())

        destination_file_name = "/tmp/{}-{}.csv".format(
            time_string, table_name)

        self.logger.info('START DOWNLOAD {} to {}.'.format(
            full_file_blob, destination_file_name))
        full_file_blob.download_to_filename(destination_file_name)
        self.logger.info('END DOWNLOAD {} to {}.'.format(
            full_file_blob, destination_file_name))
        # bug-fix removing headers from middle of file due to BlobManager bug
        MAX_ROWS = 2 * 10**6
        df = pd.read_csv(destination_file_name, '\t')
        if len(df.index) > MAX_ROWS:
            self.logger.info(
                f"Max rows exceeded ({len(df.index)}) starting search and destroy")
            column_string = df.columns[0]
            header_rows = df[df[column_string] == column_string].index
            self.logger.info(f"Removing {len(header_rows)} rows")
            df = df.drop(df[df[column_string] == column_string].index)
            self.logger.info(f"{len(header_rows)} header rows removed")
            df.to_csv(destination_file_name, sep='\t', index=False)
            time.sleep(5)
            df = pd.read_csv(destination_file_name, '\t')
        # DT-4320
        self.logger.info('STARTING TO TRUNC FIELDS.')
        # trunc string fields
        string_cols = list(df.select_dtypes(include='object').columns)
        self.logger.info(
            'TRUNCATING THE FOLLOWING FIELDS: {}'.format(string_cols))
        for col in string_cols:
            df[col] = df[col].apply(self._trunc_string)
        self.logger.info('TRUNC FIELDS COMPLETE.')

        df.to_csv(destination_file_name, sep='\t', index=False)
        self.logger.info('WROTE FILE BACK TO {}'.format(destination_file_name))

        table_schema = self.mysql_get_table_schema(
            self.mysql_connection, target_mysql_table)

        load_data_infile_query = self._query_renderer.load_data_infile(
            destination_file_name,
            database_name,
            table_name,
            table_schema.keys()
        )

        print(load_data_infile_query)
        self.logger.info('START LOAD INFILE IMPORT.')

        cursor = self.mysql_connection.cursor()

        cursor.execute(
            f"ALTER TABLE {database_name}.{table_name} DISABLE KEYS;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("SET UNIQUE_CHECKS = 0;")

        cursor.execute(load_data_infile_query)
        cursor.execute("SET UNIQUE_CHECKS = 1;")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        cursor.execute(
            f"ALTER TABLE {database_name}.{table_name} ENABLE KEYS;")

        cursor.close()

        try:
            os.remove(destination_file_name)
        except OSError:
            pass
