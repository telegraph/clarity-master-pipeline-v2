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

SCHEDULED_INTERVAL = timedelta(days=1)
START_DATE = 'None' #datetime(2020, 3, 26)
DEPEND_ON_PAST = False
CATCHUP = False

CONFIG_FILE_NAME = "clarity_master_pipeline_v2.yml"

'''notifier = email_notifier(
    models.Variable.get('SID_ALERT_SENDER_NAME'),
    models.Variable.get('SID_ALERT_SENDER_EMAIL'),
    models.Variable.get('SID_ALERT_RECIPIENTS'),
    models.Variable.get('MJ_API_KEY_PUBLIC'),
    models.Variable.get('MJ_API_KEY_SECRET')
)'''


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
        'wait_for_downstream': True
        #"on_failure_callback": notifier
    },
    "catchup": CATCHUP
}


dbt_pipeline_configuration = configuration.DBTMasterPipelineConfiguration(
    os.path.join(
        CURRENT_DIR, RuntimeConfig.CONFIG_DIR, CONFIG_FILE_NAME
    )
)


with models.DAG(MASTER_PIPELINE_NAME, **dag_args) as clarity_master_dag:
    task_list = {}
    upstream_list = {}
    downstream_list = {}


    for pipeline in dbt_pipeline_configuration.pipelines_configurations:
        clarity_task = factory.factory_dbt_task(pipeline, RuntimeConfig)
        task_list[pipeline.name] = clarity_task

        args = []
        publish_task = factory.factory_kubernetes_task('publish_'+pipeline.name,
            'eu.gcr.io/tmg-datalake/claritypublisherjob:1.0.0',
             )


'''
        if pipeline.upstreams:
            upstream_list[clarity_task.task_id] = pipeline.upstreams
        if pipeline.downstreams:
            downstream_list[clarity_task.task_id] = pipeline.downstreams

    for clarity_task_name, upstreams in upstream_list.items():
        clarity_task = task_list[clarity_task_name]
        clarity_task.set_upstream([task_list[pipeline_name] for pipeline_name in upstreams])
        clarity_task.trigger_rule = TriggerRule.ALL_SUCCESS

    for clarity_task_name, downstreams in downstream_list.items():
        clarity_task = task_list[clarity_task_name]
        clarity_task.set_downstream([task_list[pipeline_name] for pipeline_name in downstreams])
        clarity_task.trigger_rule = TriggerRule.ALL_SUCCESS
'''