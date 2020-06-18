from airflow.operators.tmg_kubernetes import TMGKubernetesPodOperator


class PipelineType:
    KUBERNETES = 'kubernetes'
    QUERY = 'query'


BIG_QUERY_CONNECTION_WITH_DRIVE_SCOPE = "bigquery_default_with_google_drive"

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
                        "tmg-etl-dev"
                    ]
                }]
            }]
        }
    }
}


def factory_dbt_task(pipeline_configuration, runtime_configuration, **kwargs):
    """
    Factory method to create dbt tasks using KubernetesPodOperator
    """
    task_id = pipeline_configuration.name
    image = pipeline_configuration.image

    dbt_vars = {'execution_date': runtime_configuration.EXECUTION_DATE}
    dbt_vars.update(pipeline_configuration.dbt_vars)
    dbt_vars.update(kwargs)
    dbt_str_vars = ', '.join([f'{k}: {v}' for k, v in dbt_vars.items()])

    docker_cmd = f"--vars \"{{ {dbt_str_vars} }}\""

    if pipeline_configuration.dbt_tag:
        docker_cmd += " --models tag:{tag} ".format(tag=pipeline_configuration.dbt_tag)

    if pipeline_configuration.dbt_target:
        docker_cmd += ' --target {}'.format(pipeline_configuration.dbt_target)

    env_vars = {
        'REPOSITORY': pipeline_configuration.git_repository,
        'PROFILE': pipeline_configuration.dbt_profile.format(**kwargs),
        'CMD': docker_cmd,
        'BRANCH': pipeline_configuration.git_branch,
        'ENVIRONMENT': pipeline_configuration.dbt_environment
    }

    return TMGKubernetesPodOperator(
        task_id=task_id,
        name=task_id,
        namespace="default",
        image=image,
        wait_for_downstream=pipeline_configuration.wait_for_downstream,
        get_logs=True,
        env_vars=env_vars,
        affinity=DEFAULT_KUBERNETES_AFFINITY,
        is_delete_operator_pod=True,
        **kwargs
    )


def factory_publisher_job(task_id, publisher_config, job_arguments):
    """
    :param task_id:
    :param publisher_config:
    :param job_arguments:
    :return:
    """
    task_config = publisher_config.task_configuration

    image_name = "eu.gcr.io/tmg-datalake/{}:{}".format(
        task_config['image_name'], task_config["version"])
    pod_arguments = ["clarityPublisherJob"] + job_arguments

    kubernetes_friendly_pod_name = task_id.replace("_", "-")

    return TMGKubernetesPodOperator(
        task_id=task_id,
        name=kubernetes_friendly_pod_name,
        namespace="default",
        image=image_name,
        get_logs=True,
        cmds=pod_arguments,
        arguments={},
        affinity=DEFAULT_KUBERNETES_AFFINITY,
        is_delete_operator_pod=True,
        env_vars={'GOOGLE_APPLICATION_CREDENTIALS':
                  publisher_config.google_app_credentials}
    )
