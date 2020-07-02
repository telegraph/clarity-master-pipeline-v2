# sidPublisherJob

### Overview

### Business goal

### Technical goal

### Repository Structure

This repository has a standard structure. 

```bash
keyscredentials/
gke_deploy/
sidPublisherJob/
tasks.py
Dockerfile
Jenkinsfile
README.md
changelog.md
```


##### keyscredentials/

This folder is where the GC credential are downloaded during the building process

##### gke_deploy/

This folder contains the kubernetes description job


##### sidPublisherJob /

This folder contains the python project with its typical structure: 
- requirements-files (dev-requirements. | requirements.txt)
- the setup.py script to install the package
- the \__version\__ module to declare the package version
- the main package (sid_dim_agent)
- run_pipeline.py which contains the entry point of the programm
- the test folder

##### tasks.py, Dockerfile, Jenkinsfile

This files are for building and deploying purpose. Normally you shouldn't change their content.

##### README.md, changelog.md

The usual `readme` and `changelog` files

### Development

Create a virtual environment in your preferred way.


The development is done inside the sidPublisherJob folder. 
Please use dev-requirements.txt to install all the necessary development packages. (pytest and invoke are included)
Feel free to add any development package you'll need since they won't be installed in the docker image.

The pipeline is created by subclassing `TMGETL` and implement it's abstract methods:

- `pre_execution_cleansing`
  This method must implement all the necessary commands to ensure this pipeline's execution is idempotent. 
  Running this pipeline multiple times with the same input MUST produce the same result in the target database.
  This method runs before the pipeline itself.

- `pipeline`
  This is where the pipeline commands should be implemented. Please keep this method clean and implement specific business login in external classes

- `post_execution_cleanup`
   This method must implement the cleanup of any temporary resource that has been created during the execution of the pipeline.
   Again, the purpose is to leave the dataset clean as it was before the pipeline execution

#### Unit Testing

Any logic implemented in python should be tested with pytest. Create test files in the `tests/` folder

For local testing:

- Activate your virtual environment
- Install the package in develop mode
```bash
$ python setup.py develop
```
- Run pytest

```bash
$ pytest tests/
```

### Run the pipeline

To run the pipeline
```bash
Usage: pipeline [OPTIONS] EXECUTION_DATE TRANSFER_NAME [truncate|delta]
                CONFIG_LOCATION

  This will run the pipeline

  EXECUTION_DATE: date of pipeline execution YYYYMMDD
  TRANSFER_NAME: pipeline name to transfer
  WRITE_MODE: Options truncate/delta
  CONFIG_LOCATION: location of config file in form gs://bucket/filename or /path/to/file

  --delta_start_date: date to backfill from YYYYMMDD

Options:
  --delta_start_date TEXT
  --help             Show this message and exit.

```

### Deployment

To deploy this repository you'll need the following:

[Invoke](https://docs.pyinvoke.org/en/1.2)

[Docker](https://www.docker.com/)

[Kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)

[Helm](https://helm.sh/)




# Invoke tasks

The following invoke commands run through cmd or terminal can create, test, and deploy the docker pipeline locally.

## create the docker image
Firstly the Docker image must be created on the local system. 
The image grabs the authentication keys from GCP when created so the download_list.txt file in the keyscredentials directory must have the relevant .json file names in it.

```
invoke make-docker-image
```

## test the docker image

The image can then be tested locally, it defaults to dev but prod can be passed as an argument. 
Execution date can be specified.
The pipeline is executed by default using your `local` environment configuration

```
invoke test-docker-local [--test-execution-date (date YYYYMMDD)]
```

## deploy the image in docker registry

If the image is tested successfully it needs to be deployed to GCP. All images are stored in the datalake. 
```
invoke deploy-docker-image
```

## deploy on kubernetes

Now that the image is in GCP, Kubernetes can use it to construct a container and test the pipeline in Kubernetes. 
Default environment is local, but can be changed. The SQL proxy can be activated by passing it as an arguement.
```
invoke local-deploy-gke [--env dev/prod] [--sql-proxy]
```
