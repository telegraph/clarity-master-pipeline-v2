import yaml
import os
from invoke import run
from invoke import task
from google.cloud import storage


pwd = os.getcwd()

PIPELINE_NAME = 'clarity-master-pipeline-v2'
DAG_NAME_FORMAT = 'clarity_master_pipeline_v2'
AIRFLOW_DIRECTORY = 'airflow'
DEV_AIRFLOW_CONFIG_BUCKET = 'europe-west2-dev-airflow-9b1988dd-bucket'
PROD_AIRFLOW_CONFIG_BUCKET = 'europe-west2-prod-airflow-66feabb0-bucket'


def get_command_stdout(command):
    result = run(command)
    return result.stdout.strip()

@task()
def update_airflow_config_deployment_tag(ctx, env, deployment_tag):

    with open('{}/{}_{}.yaml'.format(AIRFLOW_DIRECTORY, 'config', env), 'rt') as file:
        file_content = file.read()
        config = yaml.load(file_content, Loader=yaml.SafeLoader)
        config['pipeline']['tag'] = deployment_tag

    with open('{}/{}_{}.yaml'.format(AIRFLOW_DIRECTORY, 'config', env), 'w') as file:
        yaml.dump(config, file)


@task()
def upload_airflow_config_file(ctx, env, mode):

    config_gs_bucket = PROD_AIRFLOW_CONFIG_BUCKET if env == 'prod' else DEV_AIRFLOW_CONFIG_BUCKET

    storage_client = storage.Client()
    bucket = storage_client.bucket(config_gs_bucket)
    dag_name = DAG_NAME_FORMAT.format(mode)
    blob = bucket.blob('dags/etl_configs/{}/config.yaml'.format(dag_name))
    blob.upload_from_filename('{}/{}_{}_{}.yaml'.format(AIRFLOW_DIRECTORY, 'config', mode, env))


@task()
def upload_airflow_dag(ctx, env, mode):

    config_gs_bucket = PROD_AIRFLOW_CONFIG_BUCKET if env == 'prod' else DEV_AIRFLOW_CONFIG_BUCKET

    storage_client = storage.Client()
    bucket = storage_client.bucket(config_gs_bucket)
    dag_name = DAG_NAME_FORMAT.format(mode)
    blob = bucket.blob('dags/{}.py'.format(dag_name))
    blob.upload_from_filename('{}/{}.py'.format(AIRFLOW_DIRECTORY, dag_name))


@task()
def deploy_airflow(ctx, env, mode):

    upload_airflow_config_file(ctx, env, mode)
    upload_airflow_dag(ctx, env, mode)
