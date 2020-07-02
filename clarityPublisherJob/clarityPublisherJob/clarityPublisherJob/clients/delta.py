from google.cloud import bigquery
from clarityPublisherJob import BIG_QUERY_DATE_FORMAT
from clarityPublisherJob.clients.blob import BlobManager
from clarityPublisherJob.clients.transfer import TransferClient


class DeltaDirectClient(TransferClient):

    def __init__(self, bq_client, transfer, execution_date, logger):
        """
                :param BigQueryClient bq_client:
                :param TransferConfiguration transfer:
                :param datetime.datetime execution_date:
                :param logging.Logger logger:
                """

        self.transfer = transfer
        super(DeltaDirectClient, self).__init__(bq_client, self.transfer, execution_date, logger)

    def create_tmp_mysql_table_like(self, desired_table, original_table):
        """
        :param desired_table: table to create, STRING: "schema.table"
        :param original_table: table structure to copy, STRING: "schema.table"
        :return:
        """
        self.logger.info(f'First attempting to drop table: {desired_table}')
        drop_query = f'drop table {desired_table}'
        self._mysql_connect_and_run_query(self.mysql_connection, drop_query)
        self.logger.info(f'Creating tmp table on MySQL: {desired_table}')
        create_query = f'create table {desired_table} like {original_table}'
        self._mysql_connect_and_run_query(self.mysql_connection, create_query)

    def drop_indexes_from_tmp_table(self, temporary_table):

        self.logger.info("Dropping index on temporary table")
        drop_indexes_query = f"ALTER TABLE {temporary_table} "
        drop_indexes_query += ",".join([
            f"DROP INDEX {index['name']}" for index in self.transfer.table_indexes
        ])
        drop_indexes_query += ";"

        self.logger.info(drop_indexes_query)

        self._mysql_connect_and_run_query(self.mysql_connection, drop_indexes_query)

        self.logger.info("Dropped indexes")

    def replace_into_prod_mysql(self, tmp_my_sql_name, destination_table_name):
        """
        :param tmp_my_sql_name: STRING: "schema.table"
        :param destination_table_name: STRING: "schema.table"
        :return:
        """
        self._wait_for_mysql_free(self.mysql_connection)

        source_table_schema = self.mysql_get_table_schema(self.mysql_connection, tmp_my_sql_name)

        source_table_cols = ",".join(source_table_schema.keys())

        replace_query = f'replace into {destination_table_name} ({source_table_cols}) select {source_table_cols} from {tmp_my_sql_name};'

        self.logger.info(f'Running Query: {replace_query}')
        self._mysql_connect_and_run_query(self.mysql_connection, replace_query)

    def drop_fields_from_mysql(self, fields_to_drop, my_sql_name):
        """
        :param field_to_drop: List of fields to drop the MySQL Table
        :return:
        """
        for field in fields_to_drop:
            drop_fields_query = f'ALTER TABLE {my_sql_name} DROP {field};'
            self.logger.info(f'Running Query: {drop_fields_query}')
            self._mysql_connect_and_run_query(self.mysql_connection, drop_fields_query)

    def get_schema_gap(self, today_schema, raw_table_schema):
        """
        :param today_schema: current schema
        :param raw_table_schema: raw_schema
        :return: Fields which are not in today but are in raw
        """
        return [col for col in raw_table_schema if col not in today_schema]

    def run(self):

        self.logger.info('Running Delta Update Client')

        mysql_destination_table = self.transfer.mysql.destination_table
        delta_bq_table = self.transfer.bigquery.delta_direct_extract_table_name(self.execution_date)

        if not self._mysql_table_exists(self.mysql_connection, mysql_destination_table):
            raise RuntimeError(mysql_destination_table + ' MySQL TABLE DOES NOT EXIST')

        self.create_tmp_bq_new_delta()

        gs_uri = self.transfer.gcs.delta_direct_file_uri(self.execution_date)
        self.bq_to_gs(delta_bq_table, gs_uri)

        with BlobManager(self.logger, self.transfer, 'delta_direct') as concatenated_blob:

            fq_tmp_mysql_table = self.transfer.mysql.delta_direct_fqtn(self.execution_date)

            self.create_tmp_mysql_table_like(
                desired_table=fq_tmp_mysql_table,
                original_table=mysql_destination_table
            )
            self.drop_indexes_from_tmp_table(fq_tmp_mysql_table)

            if self.transfer.mysql_fields_to_drop:
                self.drop_fields_from_mysql(self.transfer.mysql_fields_to_drop, fq_tmp_mysql_table)

            self.load_data_infile(concatenated_blob, fq_tmp_mysql_table)

            self.replace_into_prod_mysql(
                tmp_my_sql_name=fq_tmp_mysql_table,
                destination_table_name=mysql_destination_table
            )

    def create_tmp_bq_new_delta(self):
        """

        :return:
        """

        replicate_mysql_query = self.build_tmp_query()

        query_job_config = bigquery.QueryJobConfig()
        query_job_config.use_legacy_sql = False

        delta_bq_table = self.transfer.bigquery.delta_direct_extract_table_name(self.execution_date)
        query_job_config.destination = self.get_table_ref(delta_bq_table)

        # Run Query and Push to tmp_table
        self.logger.info('Create Delta table in BigQuery: ' + delta_bq_table)
        self.logger.info(replicate_mysql_query)
        self.run_query(replicate_mysql_query, query_job_config)

    def build_tmp_query(self):

        source_table_schema = self.mysql_get_table_schema(
            self.mysql_connection, self.transfer.mysql.destination_table
        )

        column_to_select = [col for col in source_table_schema.keys() if col not in self.transfer.delta.fields_to_omit]

        replicate_mysql_query = self._query_renderer.delta_direct_query(
            self.execution_date.strftime(BIG_QUERY_DATE_FORMAT),
            column_to_select
        )

        return replicate_mysql_query
