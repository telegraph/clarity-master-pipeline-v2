import os
import platform
import requests
import time
from invoke import run
from invoke import task

pwd = os.getcwd()


def get_command_stdout(command):
    result = run(command)
    return result.stdout.strip()


PROJECT_NAME = 'clarityPublisherJob'
PACKAGE_NAME = 'clarityPublisherJob'
GKE_CLUSTER_NAME = "services-cluster"

DEPLOYMENT_TAG = get_command_stdout(
    'grep "__version__ = " {}/{}/version.py | cut -d"=" -f2'.format(PROJECT_NAME, PACKAGE_NAME)
).replace("'", "")


DEV_DOCKER_PROJECT = "tmg-plat-dev"
PROD_DOCKER_PROJECT = "tmg-datalake"

docker_image_name = 'eu.gcr.io/{0}/{1}:{2}'.format(PROD_DOCKER_PROJECT, PROJECT_NAME, DEPLOYMENT_TAG).lower()

KEYS_CREDENTIALS_FOLDER = 'keyscredentials'


@task
def make_docker_image(ctx):
    # Downloading key files to be moved across to Docker Image
    download_keyscredentials(ctx)

    current_prod_tag = get_latest_docker_tag(ctx)

    print('Current GCP Docker Prod Tag: ', current_prod_tag)
    print('DEPLOYMENT_TAG: ', DEPLOYMENT_TAG)

    if current_prod_tag == DEPLOYMENT_TAG:
        print('{:^100}'.format('FAILURE WHEN DEPLOYING DOCKER IMAGE TO PRODUCTION -- TAG ALREADY IN USE'), '\n',
              '{:^100}'.format('PLEASE UPDATE TAG IN SCHEDULER/PIPELINE.PROPERTIES'))
        #exit(1)

    ctx.run('docker build -t {image} .'.format(image=docker_image_name.lower()))


@task
def test_docker_local(ctx, test_execution_date=20180101):
    run_pipeline_cmd = 'docker run {docker_image_name} bash -c "python3 /task/run_pipeline.py --environment local --execution_date {execution_date} || echo failed"'
    result = ctx.run(
        run_pipeline_cmd.format(
            docker_image_name=docker_image_name,
            execution_date=test_execution_date)
    )

    if result.stdout[-7:].strip() == 'failed':
        print('Pipeline did not complete with exit code 0, consider inspecting with docker run -it {} bash'.format(
            docker_image_name))
    else:
        print('Succeeded')


@task
def deploy_docker_image(ctx):

    image_name, image_version = docker_image_name.split(":")
    result = ctx.run('docker image ls -a | grep -w {} || echo failed'.format(image_name))

    if result.stdout[-7:].strip() == 'failed':
        print('Image does not exist locally, please create the image using "invoke mk-docker-image" and test with "invoke test-docker-local"')
        return

    print('Pushing image \'{}\''.format(docker_image_name))
    ctx.run('docker push {0}'.format(docker_image_name))


@task
def get_latest_docker_tag(ctx):
    return  get_command_stdout(
        "gcloud container images list-tags eu.gcr.io/{0}/{1} | awk 'NR==2{{print $2}}'".format(
            PROD_DOCKER_PROJECT, PROJECT_NAME.lower()
        )
    )


@task
def local_deploy_gke(ctx, env='dev', execution_date=20190708, transfer_name='dim_account_pipeline', write_mode='delta', backfill_date=None, config_location=None):
    """
    Deploys the container into kubernetes

    :param ctx:
    :param env:
    :param execution_date:
    :return:
    """

    if env == 'dev':
        project_to_deploy = DEV_DOCKER_PROJECT
    elif env == 'prod':
        project_to_deploy = PROD_DOCKER_PROJECT
    else:
        raise NotImplemented("Can't run this command on {} environment".format(env))

    gke_context = get_command_stdout(
        "kubectl config get-contexts | grep {} | grep {} | awk -F' ' '{{print $2}}'".format(
            project_to_deploy,
            GKE_CLUSTER_NAME
        )
    )

    print('gke_context: ', gke_context)

    ctx.run('kubectl config use-context {}'.format(gke_context))

    with ctx.cd('./gke_deploy/'):

        helm_command = "helm install --name={pipeline_name} . --values=./profiles/{env}.yaml --set-string"
        helm_command += ' execution_date="{execution_date}",image_tag="{tag}",package_name="{package_name}",'
        helm_command += 'transfer_name="{transfer_name}",write_mode="{write_mode}",backfill_date="{backfill_date}",'
        helm_command += 'config_location="{config_location}"'

        print(helm_command.format(
            pipeline_name=PROJECT_NAME.lower(),
            env=env,
            tag=DEPLOYMENT_TAG,
            execution_date=execution_date,
            package_name=PACKAGE_NAME,
            transfer_name=transfer_name,
            write_mode=write_mode,
            backfill_date=backfill_date if backfill_date else '',
            config_location=config_location if config_location else ''
        ))
        ctx.run(helm_command.format(
            pipeline_name=PROJECT_NAME.lower(),
            env=env,
            tag=DEPLOYMENT_TAG,
            execution_date=execution_date,
            package_name=PACKAGE_NAME,
            transfer_name=transfer_name,
            write_mode=write_mode,
            backfill_date=backfill_date if backfill_date else '',
            config_location=config_location if config_location else ''
        ))

    print("Job Deployed to Kubernetes, run this command to view logs locally:")
    print('kubectl config use-context {}'.format(gke_context))
    print("kubectl logs jobs/{} --follow=True".format(PROJECT_NAME.lower()))

    print("Delete the Job from Helm Tiller on Kubernetes:\n\n")
    print("helm del --purge {}\n\n".format(PROJECT_NAME))
    print("If the pipeline failed because the container image is broken please consider running:\n\n")
    print("`invoke delete-failed-container-image`\n")
    print("PLEASE NOTE: THIS WILL REMOVE THE DOCKER CONTAINER FROM THE CONTAINER REGISTRY'")


@task
def delete_failed_container_image(ctx):

    digest_to_delete = get_command_stdout("gcloud container images list-tags eu.gcr.io/{}/{} \
    --filter='tags:{tag}' --format='get(digest)'".format(
        PROD_DOCKER_PROJECT, PROJECT_NAME, tag=DEPLOYMENT_TAG
    ))

    ctx.run("gcloud container images delete --quiet eu.gcr.io/{}/{}@{digest} --force-delete-tags".format(
        PROD_DOCKER_PROJECT, PROJECT_NAME, digest=digest_to_delete
    ))


@task
def download_keyscredentials(ctx):
    files_to_download = []
    FULL_KEYS_CREDENTIALS_FOLDER = '{}/{}'.format(pwd, KEYS_CREDENTIALS_FOLDER)
    with open('{}/download_list.txt'.format(FULL_KEYS_CREDENTIALS_FOLDER)) as download_file_list:
        for file in download_file_list:
            files_to_download.append(file.strip())

    for file in files_to_download:
        print('Downloading {} to {} folder'.format(file, KEYS_CREDENTIALS_FOLDER))
        ctx.run('gsutil cp gs://tmg-datalake-admin/{file} {destination}'.format(
            file=file,
            destination=FULL_KEYS_CREDENTIALS_FOLDER
        ))


def _install_brew(ctx):
    """
    Installing Brew
    """

    result = ctx.run("brew help", hide=True)
    if result.failed:
        ctx.run('/usr/bin/ruby -e "$(curl e-fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"')


def _install_docker(ctx):
    """
    Installing Docker
    """

    result = ctx.run("docker help", hide=True)
    if result.failed:
        ctx.run('')
