import datetime as dt

import mysql.connector
from clarityPublisherJob.clients.blob import BlobManager
from clarityPublisherJob.clients.transfer import TransferClient


class TruncateClient(TransferClient):

    def __init__(self, bq_client, transfer, execution_date, logger):
        """
        This type of transfer create a full refresh by truncating the mysql table
        and by copying the whole bq table

        :param BigQueryClient bq_client:
        :param TransferConfiguration transfer:
        :param datetime.datetime execution_date:
        :param logging.Logger logger:
        """

        self.transfer = transfer
        super(TruncateClient, self).__init__(bq_client, self.transfer, execution_date, logger)

        self.yesterday = execution_date - dt.timedelta(days=1)

        self.my_sql_connection = mysql.connector.connect(
            host=self.transfer.mysql.host,
            user=self.transfer.mysql.user,
            passwd=self.transfer.mysql.password,
            database=self.transfer.mysql.schema
        )
        self.my_sql_connection.autocommit = True

    def run(self):

        self.logger.info('Running Truncate Client')
        if not self._mysql_table_exists(
                self.my_sql_connection,
                self.transfer.mysql.destination_table
        ):
            raise RuntimeError(self.transfer.mysql.destination_table + ' MySQL TABLE DOES NOT EXIST')

        gs_uri = self.transfer.gcs.extract_file_uri(self.execution_date)
        self.bq_to_gs(self.transfer.bigquery.bq_full_table_name, gs_uri)

        with BlobManager(self.logger, self.transfer) as blob:
            self.truncate_table()
            self.load_data_infile(blob, self.transfer.mysql.destination_table)

    def truncate_table(self):
        """

        :return:
        """
        self.logger.info(f'Truncating table {self.transfer.mysql.destination_table}')

        truncate_query = f"TRUNCATE TABLE {self.transfer.mysql.destination_table};"
        self._mysql_connect_and_run_query(self.my_sql_connection, truncate_query)

    def clean_indices(self):
        """
        Remove the indexes from the table
        :return:
        """

        for index_name, query in self.build_drop_index_list(self.transfer).items():
            self.logger.info(f"Removing index: {index_name}, on table {self.transfer.mysql.destination_table}")
            self._mysql_connect_and_run_query(self.my_sql_connection, query)

    @staticmethod
    def build_drop_index_list(transfer):
        """
        Create a list of 'DROP INDEX' sql queries
        :param TransferConfiguration transfer:
        :return dict :
        """

        drop_indexes_queries = {}
        for index in transfer.table_indexes:
            index_name = index['name']

            drop_indexes_queries[index_name] = "DROP INDEX {index_name} ON {mysql_table};".format(
                index_name=index_name,
                mysql_table=transfer.mysql.destination_table
            )

        return drop_indexes_queries

    def recreate_indices(self):
        """

        :return:
        """
        for key, query in self.build_create_index_list(self.transfer).items():
            index_name, column_list = key

            msg = "Creating index: {} on column {} on table {}".format(
                index_name,
                column_list,
                self.transfer.mysql.destination_table
            )

            self.logger.info(msg)
            self._mysql_connect_and_run_query(self.my_sql_connection, query)

    @staticmethod
    def build_create_index_list(transfer):
        """

        :param TransferConfiguration transfer:
        :return dict:
        """
        create_index_queries = {}
        for index in transfer.table_indexes:
            index_name = index['name']
            column_list = index['columns']

            create_index_queries[
                (index_name, column_list)
            ] = "CREATE INDEX {index_name} ON {mysql_table} ({columns});".format(
                index_name=index_name,
                mysql_table=transfer.mysql.destination_table,
                columns=column_list
            )

        return create_index_queries
