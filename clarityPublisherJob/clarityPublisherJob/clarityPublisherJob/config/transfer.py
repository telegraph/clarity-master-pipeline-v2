from clarityPublisherJob import DATE_FORMAT

DEFAULT_MOST_RECENT_IDENTIFIER = "RAW_TABLE.PARTITION_FIELD_DATE"


class TransferMysqlConfiguration:

    def __init__(self, mysql_configuration, transfer_mysql_table):
        """

        :param dict mysql_configuration:
        :param TransferConfiguration transfer:
        """
        self.instance_name = mysql_configuration['instance_name']
        self.host = mysql_configuration['host']
        self.user = mysql_configuration['user']
        self.password = mysql_configuration['password']

        self.schema = mysql_configuration['database']
        self.table = transfer_mysql_table
        self.tmp_mysql_schema = mysql_configuration['tmp_mysql_schema']

        self._delta_new_table_template = "{table_name}_delta_{exec_date}"
        self._delta_update_table_template = "{table_name}_update_{exec_date}"
        self._delta_direct_table_template = "{table_name}_delta_direct_{exec_date}"

    @property
    def sanity_check_query(self):
        return "SELECT COUNT(*) as count FROM `{}`".format(
            self.table
        )

    @property
    def destination_table(self):
        return f'{self.schema}.{self.table}'

    def delta_new_fqtn(self, execution_date):
        table_name = self._delta_new_table_template.format(
            table_name=self.table,
            exec_date=execution_date.strftime(DATE_FORMAT)
        )
        return '{}.{}'.format(
            self.tmp_mysql_schema,
            table_name
        )

    def delta_update_fqtn(self, execution_date):
        table_name = self._delta_update_table_template.format(
            table_name=self.table,
            exec_date=execution_date.strftime(DATE_FORMAT)
        )
        return '{}.{}'.format(
            self.tmp_mysql_schema,
            table_name
        )

    def delta_direct_fqtn(self, execution_date):
        table_name = self._delta_direct_table_template.format(
            table_name=self.table,
            exec_date=execution_date.strftime(DATE_FORMAT)
        )
        return '{}.{}'.format(
            self.tmp_mysql_schema,
            table_name
        )


class TransferBigQueryConfiguration:

    def __init__(self, project, big_query_configuration, transfer):
        """

        :param str project:
        :param dict big_query_configuration:
        :param TransferConfiguration transfer:
        """
        self.project = project
        self.sanity_check_dataset = big_query_configuration['sanity_check_dataset']
        self.sanity_check_table = big_query_configuration['sanity_check_table']

        self.dataset = big_query_configuration['dataset']
        self.delta_dataset = big_query_configuration['delta_dataset']

        self._delta_new_extract_table_form = "{table_name}_delta_new_{date}"
        self._delta_update_extract_table_form = "{table_name}_delta_update_{date}"
        self._delta_direct_extract_table_form = "{table_name}_delta_direct_{date}"

        self._transfer = transfer
        self.table_name = self._transfer.bq_table
        self.key = self._transfer.bq_key

    @property
    def sanity_check_query(self):
        return "SELECT COUNT(*) as count FROM `{}`".format(
            self.bq_full_table_name
        )

    @property
    def bq_full_table_name(self):
        return f'{self.project}.{self._transfer.bq_dataset}.{self._transfer.bq_table}'

    @property
    def bq_full_raw_table_name(self):
        if self._transfer.bq_raw_table:
            return '{}.{}.{}'.format(
                self.project,
                self.dataset,
                self._transfer.bq_raw_table
            )
        else:
            raise ValueError(f"Raw table for {self._transfer.name} not set.")

    def delta_new_bq_table_name(self, execution_date):

        table_name = self._delta_new_extract_table_form.format(
            table_name=self.table_name,
            date=execution_date.strftime(DATE_FORMAT)
        )
        return '{}.{}.{}'.format(
            self.project,
            self.delta_dataset,
            table_name
        )

    def delta_update_bq_table_name(self, execution_date):
        table_name = self._delta_update_extract_table_form.format(table_name=self._transfer.bq_table,
                                                                  date=execution_date.strftime(DATE_FORMAT))
        return '{}.{}.{}'.format(
            self.project,
            self.delta_dataset,
            table_name
        )

    def delta_direct_extract_table_name(self, execution_date):

        table_name = self._delta_direct_extract_table_form.format(
            table_name=self.table_name,
            date=execution_date.strftime(DATE_FORMAT)
        )

        return '{}.{}.{}'.format(
            self.project,
            self.delta_dataset,
            table_name
        )


class TransferGSConfiguration:
    TEMPLATE_EXTRACT_FILENAME = "/{table_name}_{date}"
    TEMPLATE_EXTRACT_DELTA_NEW_FILENAME = "/delta_new_{table_name}_delta_{date}"
    TEMPLATE_EXTRACT_DELTA_DIRECT_FILENAME = "/delta_direct_{table_name}_delta_direct_{date}"
    TEMPLATE_EXTRACT_DELTA_UPDATE_FILENAME = "/delta_update_{table_name}_update_{date}"

    def __init__(self, gcs_configuration, transfer):
        """
        :param dict gcs_configuration:
        :param TransferConfiguration transfer:
        """
        self.bucket = gcs_configuration['bucket']
        self.file_ending = gcs_configuration['file_ending']

        self.bucket_url = "gs://" + self.bucket

        self._extract_file_form = self.bucket_url + self.TEMPLATE_EXTRACT_FILENAME
        self._delta_new_extract_file_form = self.bucket_url + self.TEMPLATE_EXTRACT_DELTA_NEW_FILENAME
        self._delta_update_extract_file_form = self.bucket_url + self.TEMPLATE_EXTRACT_DELTA_UPDATE_FILENAME
        self._delta_direct_file_form = self.bucket_url + self.TEMPLATE_EXTRACT_DELTA_DIRECT_FILENAME

        self._transfer = transfer

    @property
    def extract_file_prefix(self):
        return "{}_".format(self._transfer.bq_table)

    def extract_file_uri(self, execution_date):
        return self._extract_file_form.format(
            table_name=self._transfer.bq_table,
            date=execution_date.strftime(DATE_FORMAT)
        )

    def delta_new_extract_file_uri(self, execution_date):
        return self._delta_new_extract_file_form.format(
            table_name=self._transfer.bq_table,
            date=execution_date.strftime(DATE_FORMAT)
        )

    def delta_update_extract_file_uri(self, execution_date):
        return self._delta_update_extract_file_form.format(
            table_name=self._transfer.bq_table,
            date=execution_date.strftime(DATE_FORMAT)
        )

    def delta_direct_file_uri(self, execution_date):
        return self._delta_direct_file_form.format(
            table_name=self._transfer.bq_table,
            date=execution_date.strftime(DATE_FORMAT)
        )


class DeltaTransferConfiguration:

    def __init__(self, delta_transfer_configuration):
        """

        :param dict delta_transfer_configuration:
        """
        self.fields_to_omit = delta_transfer_configuration['fields_to_omit']
        self.most_recent_identifier = delta_transfer_configuration.get('most_recent_identifier',
                                                                       DEFAULT_MOST_RECENT_IDENTIFIER)


class TransferConfiguration:
    TRANSFER_DELTA = 'delta'
    TRANSFER_TRUNCATE = 'truncate'

    def __init__(self, project, name,
                 transfer_configuration,
                 mysql_configuration,
                 bigquery_configuration,
                 gcs_configuration
                 ):
        """

        :param str project:
        :param str name:
        :param dict transfer_configuration:
        :param dict mysql_configuration:
        :param dict bigquery_configuration:
        :param dict gcs_configuration:
        """
        self.project = project

        self.name = name

        self.bq_table = transfer_configuration['bq_table']

        transfer_config = transfer_configuration.get('transfer')

        self._load_data_infile = transfer_config['load_data_infile']

        self._transfer_method = transfer_config['method']

        #DV-4360 added seperate load files for each table - possible change to more advanced template
        self.load_data_infile = transfer_config['load_data_infile']

        if self._transfer_method == self.TRANSFER_DELTA:
            self.delta = DeltaTransferConfiguration(transfer_config)
        else:
            self.delta = None

        self.bq_raw_table = transfer_configuration.get('bq_raw_table')
        self.bq_key = transfer_configuration.get('bq_key')
        self.bq_raw_table_partitions = transfer_configuration.get('bq_raw_table_partitions')

        self.max_partition_day_retries = transfer_configuration.get('max_partition_day_retries', 5)

        self.table_indexes = transfer_configuration.get('table_indexes', [])
        self.mysql_fields_to_drop = transfer_configuration.get('mysql_fields_to_drop', [])

        self.mysql = TransferMysqlConfiguration(mysql_configuration, transfer_configuration['mysql_table'])
        self.bigquery = TransferBigQueryConfiguration(self.project, bigquery_configuration, self)
        self.gcs = TransferGSConfiguration(gcs_configuration, self)

    @property
    def is_delta(self):
        return self._transfer_method == self.TRANSFER_DELTA

    @property
    def is_truncate(self):
        return self._transfer_method == self.TRANSFER_TRUNCATE

    @property
    def bq_dataset(self):
        return self.bigquery.dataset

    @property
    def mysql_schema(self):
        return self.mysql.schema
