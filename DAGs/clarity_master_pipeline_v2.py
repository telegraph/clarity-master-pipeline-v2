"""
Clarity V2 Master Pipeline DAG
"""
from datetime import datetime, timedelta
import os

from airflow import models
from airflow.operators.sensors import ExternalTaskSensor
from airflow.utils.trigger_rule import TriggerRule

import clarity_library.factory as factory
import clarity_library.configuration as configuration
from clarity_library.utilities import email_notifier

MASTER_PIPELINE_NAME = os.path.basename(os.path.splitext(__file__)[0])
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

SCHEDULED_INTERVAL = '30 7 * * *'
START_DATE = datetime(2020, 10, 8)
DEPEND_ON_PAST = True
CATCHUP = True

CONFIG_FILE_NAME = "clarity_master_pipeline_v2_{}.yml".format(
    models.Variable.get('env'))

notifier = email_notifier(
    'Airflow Failure Alert',
    models.Variable.get('EMAIL_ALERT_SENDER'),
    models.Variable.get('EMAIL_ALERT_RECIP'),
    models.Variable.get('MJ_API_KEY_PUBLIC'),
    models.Variable.get('MJ_API_KEY_SECRET')
)


class RuntimeConfig:
    DATE_FORMAT_SHORT = "%Y%m%d"

    EXECUTION_DATE = "{{ ds_nodash }}"

    DOCKER_REGISTRY = "eu.gcr.io/tmg-datalake/"
    CONFIG_DIR = "clarity-config"
    #QUERY_DIR = "queries"


dag_args = {
    "schedule_interval": SCHEDULED_INTERVAL,
    "default_args": {
        "start_date": START_DATE,
        "depends_on_past": DEPEND_ON_PAST,
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "project_id": models.Variable.get("gcp_project"),
        'wait_for_downstream': False
        # "on_failure_callback": notifier
    },
    "catchup": CATCHUP,
    'max_active_runs': 1
}


dbt_pipeline_configuration = configuration.DBTMasterPipelineConfiguration(
    os.path.join(
        CURRENT_DIR, RuntimeConfig.CONFIG_DIR, CONFIG_FILE_NAME
    )
)


publisher_config = configuration.MysqlPublisherJobConfiguration(
    os.path.join(CURRENT_DIR, RuntimeConfig.CONFIG_DIR, CONFIG_FILE_NAME)
)

with models.DAG(MASTER_PIPELINE_NAME, **dag_args) as clarity_master_dag:
    task_list = {}
    upstream_list = {}
    downstream_list = {}

    for pipeline in dbt_pipeline_configuration.pipelines_configurations:
        clarity_task = factory.factory_dbt_task(pipeline, RuntimeConfig)
        task_list[pipeline.name] = clarity_task
        clarity_task.trigger_rule = TriggerRule.ALL_SUCCESS

        if pipeline.downstreams:
            downstream_list[clarity_task.task_id] = pipeline.downstreams

        # linking publish tasks to pipeline tasks
        for pipeline_name, publisher_jobs in publisher_config.job_list.items():

            matching_publish_tasks = []
            if pipeline.name == pipeline_name:

                for publisher_job in publisher_jobs:

                    job_arguments = [
                        RuntimeConfig.EXECUTION_DATE,
                        publisher_job.transfer_name,
                        publisher_config.configuration_file

                    ]

                    clarity_publisher_task = factory.factory_publisher_job(
                        task_id='{}-mysql-publisher-job'.format(
                            publisher_job.transfer_name),
                        publisher_config=publisher_config,
                        job_arguments=job_arguments
                    )
                    clarity_publisher_task.trigger_rule = TriggerRule.ALL_SUCCESS

                    matching_publish_tasks.append(clarity_publisher_task)

                    # adding publish tasks that are downstream of other publish taskds
                    if publisher_job.downstreams:

                        # changing the transfer name to the downstream task name
                        job_arguments[1] = publisher_job.downstreams

                        clarity_publisher_task_ds = factory.factory_publisher_job(
                            task_id='{}-mysql-publisher-job'.format(
                                publisher_job.downstreams),
                            publisher_config=publisher_config,
                            job_arguments=job_arguments)

                        clarity_publisher_task_ds.trigger_rule = TriggerRule.ALL_SUCCESS
                        clarity_publisher_task.set_downstream(
                            clarity_publisher_task_ds)

            clarity_task.set_downstream(matching_publish_tasks)

    for clarity_task_name, downstreams in downstream_list.items():
        clarity_task = task_list[clarity_task_name]
        clarity_task.set_downstream(
            [task_list[pipeline_name] for pipeline_name in downstreams])
        clarity_task.trigger_rule = TriggerRule.ALL_SUCCESS
