import datetime

import mysql.connector
from google.cloud import bigquery
from clarityPublisherJob.biquery import BigQueryClient


class SanityCheck:

    def __init__(self, logger, transfer):
        """

        :param Logger logger:
        :param TransferConfiguration transfer:
        :param datetime.datetime execution_date:
        """
        self.transfer = transfer
        self.logger = logger

        self.my_sql_connection = mysql.connector.connect(
            host=self.transfer.mysql.host,
            user=self.transfer.mysql.user,
            passwd=self.transfer.mysql.password,
            database=self.transfer.mysql.schema
        )

        self._bigquery_client = BigQueryClient(self.transfer.project)

    def run(self):
        """
        Runs sanity check between source (BQ) and destination table (MySQL).
        """

        mysql_result = self._count_mysql_rows()
        bq_result = self._count_bigquery_rows()

        discrepancy = mysql_result - bq_result

        self._store_result(discrepancy)

        return discrepancy

    def _count_bigquery_rows(self):
        """
        Count rows on big query for the table
        :return:
        """
        self.logger.info('Getting Count of Records on BQ')
        bq_result = self._bigquery_client.run_query(
            self.transfer.bigquery.sanity_check_query,
            bigquery.QueryJobConfig(),
            return_results=True
        )['data'][0][0]

        self.logger.info(f'BQ Row Count: {bq_result}')

        return bq_result

    def _count_mysql_rows(self):
        """
        Counts the rows on mysql for the table

        :return:
        """
        self.logger.info('Getting Count of Records on MySQL')

        cursor = self.my_sql_connection.cursor()
        query = self.transfer.mysql.sanity_check_query
        self.logger.info(query)
        cursor.execute(query)
        mysql_result = cursor.fetchall()[0][0]
        self.my_sql_connection.close()

        self.logger.info(f'MySQL Row Count: {mysql_result}')
        return mysql_result

    def _store_result(self, discrepancy):
        """
        Stores result of sanity check in given bigquery table
        """
        dataset = self.transfer.bigquery.sanity_check_dataset
        table = self.transfer.bigquery.sanity_check_table

        table_ref = self._bigquery_client.dataset(dataset).table(table)
        table = self._bigquery_client.get_table(table_ref)  # API request

        row = (
            str(datetime.datetime.now()),
            self.transfer.name,
            self.transfer.bigquery.table_name,
            discrepancy,
            'success'
        )

        rows_to_insert = [row]
        self.logger.info('Inserting discrepancy row to BQ')
        self._bigquery_client.insert_rows(table, rows_to_insert)
