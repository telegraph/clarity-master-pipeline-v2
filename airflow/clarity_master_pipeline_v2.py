import datetime
import os
import yaml

from airflow import models, macros
from airflow.operators.dummy_operator import DummyOperator
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from tmg_library.notification import notify
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

PACKAGE_NAME = 'clarity_master_pipeline_v2'
CURRENT_DIR = "/home/airflow/gcs/dags"
CONFIG_DIR = "etl_configs/{}".format(PACKAGE_NAME)
CONFIG_FILE = "config.yaml"


with open(os.path.join(CURRENT_DIR, CONFIG_DIR, CONFIG_FILE)) as config:
    yaml_loaded = yaml.load(config, Loader=yaml.FullLoader)
    pipelines = yaml_loaded['pipelines']
    dag_arguments = yaml_loaded['default_args']


START_DATE = datetime.datetime.strptime(dag_arguments['starting_date'], '%Y%m%d')


DEFAULT_KUBERNETES_AFFINITY = {
    "nodeAffinity": {
        # requiredDuringSchedulingIgnoredDuringExecution means in order
        # for a pod to be scheduled on a node, the node must have the
        # specified labels. However, if labels on a node change at
        # runtime such that the affinity rules on a pod are no longer
        # met, the pod will still continue to run on the node.
        "requiredDuringSchedulingIgnoredDuringExecution": {
            "nodeSelectorTerms": [{
                "matchExpressions": [{
                    # When nodepools are created in Google Kubernetes
                    # Engine, the nodes inside of that nodepool are
                    # automatically assigned the label
                    # "cloud.google.com/gke-nodepool" with the value of
                    # the nodepool"s name.
                    "key": "cloud.google.com/gke-nodepool",
                    "operator": "In",
                    # The label key"s value that pods can be scheduled
                    # on.
                    "values": [
                        models.Variable.get('node_pool')
                    ]
                }]
            }]
        }
    }
}

default_dag_args = {"start_date": START_DATE,
                    "email_on_failure": True,
                    "email_on_retry": False,
                    "retries": dag_arguments['retries'],
                    "retry_delay": datetime.timedelta(minutes=dag_arguments['delay']),
                    "project_id": models.Variable.get("gcp_project"),
                    "depends_on_past": True}


with models.DAG(dag_id=PACKAGE_NAME,
                default_args=default_dag_args,
                schedule_interval=dag_arguments['schedule_interval'],
                catchup=dag_arguments['catchup'],
                max_active_runs=1) as dag:

    operators = {}
    for pipeline_name, value in pipelines.items():
        operators[pipeline_name] = KubernetesPodOperator(
            task_id=pipeline_name,
            name=pipeline_name,
            image='{0}:{1}'.format(value['image'], value['tag']),
            namespace="default",
            get_logs=True,
            affinity=DEFAULT_KUBERNETES_AFFINITY,
            is_delete_operator_pod=True,
            on_failure_callback=notify,
        )

        shard_date = "{{ macros.ds_format(macros.ds_add(ds, 1), '%Y-%m-%d', '%Y%m%d') }}"
        dbt_vars = {}
        for arg in value['args']:
            for k, v in arg.items():
                dbt_vars[k] = v
        dbt_vars['shard_date'] = shard_date

        dbt_str_vars = ', '.join([f"'{k}': '{v}'" for k, v in dbt_vars.items()])
        cmds = [
            "dbt", "run",
            "--vars", "{{ {dbt_str_vars} }}".format(dbt_str_vars=dbt_str_vars),
            "--target", "{}".format(models.Variable.get('env')),
            "--profiles-dir", "."
        ]

        extra_cmds = value.get('extra_cmds', None)
        if extra_cmds:
            cmds = cmds + extra_cmds
        operators[pipeline_name].cmds = cmds

    dummy = DummyOperator(task_id='start')

    dummy >> operators['dim_spark_campaigns']

    operators['dim_spark_campaigns'] >> operators['dfp']
    operators['dim_spark_campaigns'] >> operators['competition_formstack']
    operators['dim_spark_campaigns'] >> operators['video_youtube']
    operators['dim_spark_campaigns'] >> operators['tcuk']

    operators['tcuk'] >> operators['dim_spark_campaigns_urls']

    operators['dim_spark_campaigns_urls'] >> operators['applenews']
    operators['dim_spark_campaigns_urls'] >> operators['liveapp']
    operators['dim_spark_campaigns_urls'] >> operators['editionapp']
    operators['dim_spark_campaigns_urls'] >> operators['article_tcuk']

    operators['applenews'] >> operators['article_applenews']

