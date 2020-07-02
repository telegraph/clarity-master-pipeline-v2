class QueryRenderer:

    def __init__(self, jinja_env, transfer):
        """

        :param jinja2.Environment jinja_env:
        """
        self._jinja = jinja_env
        self.transfer = transfer
        self.load_file_name = self.transfer._load_data_infile

    def delta_direct_query(self, date, columns_to_select):
        """

        :param str date date: big query date string
        :param list columns_to_select:
        :return:
        """

        template = self._jinja.get_template('delta_direct.sql')

        return template.render(
            raw_table=self.transfer.bigquery.bq_full_raw_table_name,
            date=date,
            most_recent_identifier=self.transfer.delta.most_recent_identifier,
            columns_to_select=columns_to_select,
            table_key=self.transfer.bigquery.key
        )

    def load_data_infile(self, data_file_path, table_schema, table_name, field_list):
        template = self._jinja.get_template(self.load_file_name)

        return template.render(
            data_file_path=data_file_path,
            table_schema=table_schema,
            table_name=table_name,
            field_list=field_list
        )
