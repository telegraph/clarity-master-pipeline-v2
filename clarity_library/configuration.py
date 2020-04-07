from collections import namedtuple
from copy import copy

import yaml


class DBTConfiguration:
    def __init__(self, dbt_configuration_dictionary):
        """
        :param dict dbt_configuration_dictionary:
        """
        self.repositories = copy(dbt_configuration_dictionary['repositories'])
        self.profile = dbt_configuration_dictionary['profile']
        self.image = dbt_configuration_dictionary['image']
        self.environment = dbt_configuration_dictionary['environment']


class DBTPipelineConfiguration:
    def __init__(self, name, dbt_pipeline_dictionary, dbt_configuration):
        """
        :param dict dbt_pipeline_dictionary:
        :param DBTConfig dbt_configuration:
        """
        self.name = name
        self.type = dbt_pipeline_dictionary['type']
        self.image = dbt_configuration.image

        repository_name = dbt_pipeline_dictionary['git_repository']
        self.git_repository = dbt_configuration.repositories[repository_name]

        self.git_branch = dbt_pipeline_dictionary['git_branch']
        self.dbt_vars = dbt_pipeline_dictionary.get('dbt_vars', {})
        self.dbt_tag = dbt_pipeline_dictionary['dbt_tag']
        self.dbt_profile = dbt_configuration.profile
        self.dbt_target = dbt_pipeline_dictionary.get('dbt_target')
        self.dbt_environment = dbt_configuration.environment
        self.wait_for_downstream = bool(dbt_pipeline_dictionary.get('wait_for_downstream'))

        self.upstreams = copy(dbt_pipeline_dictionary.get('af_upstreams', []))
        self.downstreams = copy(dbt_pipeline_dictionary.get('af_downstreams', []))


class DBTMasterPipelineConfiguration:
    def __init__(self, dbt_config_filename):
        with open(dbt_config_filename) as config_file:
            yaml_content = yaml.load(config_file.read(), Loader=yaml.SafeLoader)

        self.dbt_configuration = DBTConfiguration(yaml_content['dbt'])
        self.pipelines_configurations = []

        for pipeline_name, pipeline_config in yaml_content['pipelines'].items():
            self.pipelines_configurations.append(
                DBTPipelineConfiguration(pipeline_name, pipeline_config, self.dbt_configuration)
            )

# added downsteams to named tuple for cases where publisher job needs to link to another 
MysqlPublisherJob = namedtuple('MysqlPublisherJob', 'name transfer_name full_refresh downstreams')

class MysqlPublisherJobConfiguration:

    def __init__(self, mysql_publisher_job_filename):
        self.job_list = {}
        self.image = None
        self.image_version = None
        self.configuration_file = None
        self.google_app_credentials = None

        yaml_content = self._read_file(mysql_publisher_job_filename)

        self._populate(yaml_content)

    def _read_file(self, mysql_publisher_file_name):
        with open(mysql_publisher_file_name) as config_file:
            yaml_content = yaml.load(config_file.read(), Loader=yaml.SafeLoader)
        return yaml_content

    def _populate(self, configuration):
        self.image = configuration['publisher']['image']
        self.image_version = configuration['publisher']['version']
        self.configuration_file = configuration['publisher']['configuration_file']
        self.google_app_credentials = configuration['publisher']['google_app_credentials']

        for pipeline_name, publisher_config_list in configuration['publisher']['pipelines'].items():
            self.job_list[pipeline_name] = []
            for publisher_config in publisher_config_list:
                publisher_job = MysqlPublisherJob(pipeline_name,
                                                  publisher_config['transfer_name'],
                                                  publisher_config.get('full_refresh', False),
                                                  publisher_config.get('af_downstreams', False) #added
                                                  )

                self.job_list[pipeline_name].append(publisher_job)

    @property
    def task_configuration(self):
        return {
            "image_name": self.image,
            "version": self.image_version
        }
