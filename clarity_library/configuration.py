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
