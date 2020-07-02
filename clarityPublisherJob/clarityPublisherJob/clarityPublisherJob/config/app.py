from clarityPublisherJob.config.transfer import TransferConfiguration


class ApplicationConfig:

    def __init__(self, global_configuration, logger):
        """
        Global application config. It models the full config file and contains the sub configs for each transfer.

        :param dict global_configuration:
        :param tmg_etl_library.cloud_logger.cloud_logger.Logger logger:
        """

        self.logger = logger
        self.project = global_configuration['project']
        self.push_logger_to_pubsub = global_configuration['logger']['push_to_pubsub']

        self.pub_sub_subscription_name = global_configuration['pubsub']['subscription_name']
        self.mysql = global_configuration['mysql']
        self.bq = global_configuration['bq']
        self.gcs = global_configuration['gcs']

        self.transfers = {}

        for name, values in global_configuration['transfers'].items():
            try:
                transfer = TransferConfiguration(
                    self.project,
                    name,
                    values,
                    self.mysql,
                    self.bq,
                    self.gcs
                )

                self.transfers[name] = transfer
            except KeyError:
                logger.error(f"Error reading the configuration of transfer: {name}")

    def get_transfer(self, name):
        return self.transfers[name]
