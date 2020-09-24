# clarity-master-pipeline-v2
Repository for Clarity v2 deployment to Airflow 

## Overview 
Clarity is a dashboard that houses advertising related data and metrics that we offer to our advertising clients so they can keep track on how their ads are performing on our media platforms. It currently collects and aggregates data from Telegraph.co.uk, Edions App, News App, Apple News and various video hosting platforms. This project contains the logic that runs clarity back end data pipelines.
The DAG is designed read a yml file and automatically pick up new tasks (pipelines) to run. 

[![clarity-v2-dag.png](https://i.postimg.cc/1RJTp8n2/clarity-v2-dag.png)](https://postimg.cc/QVK0DxqJ)

## Project Structure 
The project is separated into three main sections 
### DAGs
This houses the DAG that is run on ariflow (edit with caution)
> **Airflow** - This is the platform where the project is run. For more information see the tech document https://docs.google.com/document/d/1wtDsqWfdBqoRhQtSXFTMaEGhKyynrOfdoveSh8b0KWM/edit# 

### clarityPublisherJob
This folder contains the logic that migrates tables from BigQuery into CloudSQL. It is based of the SID publisherJob. It needs to be dockerised and deployed to the container registory. 

### clarity_library
This folder contains some helpful modules used by the DAG in order to configure tasks. It aslo contains the most important file in the project which is the **clarity_master_pipeline_v2_{env}.yml**
This file is the controller for the entire pipeline and should be the only file that needs to be updated when making changes to the pipeline. 

Each of the pipeline that are run my Clarity V2 can be found below

* [Dim Spark Campaigns!](https://github.com/telegraph/clarity-dim-spark-campaigns-pipeline/tree/DV-4316)
* [DFP!](https://github.com/telegraph/clarity-dfp-pipeline/tree/DT-4323)
* [Ooyala Youtube!](https://github.com/telegraph/clarity-ooyala-youtube-pipeline/tree/DT-4325)
* [Teads!](https://github.com/telegraph/clarity-teads-pipeline/tree/DT-4329)
* [Formstack!](https://github.com/telegraph/clarity-formstack-pipeline/tree/DT-4332)
* [Wayin!](https://github.com/telegraph/clarity-wayin-pipeline/tree/DT-4335)
* [TCUK!](https://github.com/telegraph/clarity-tcuk-pipeline/tree/DT-4345)
* [NewsApp!](https://github.com/telegraph/clarity-newsapp-pipeline/tree/DT-4375)
* [Twipe!](https://github.com/telegraph/clarity-twipe-pipeline)
* [AppleNews!](https://github.com/telegraph/clarity-applenews-pipeline/tree/DT-4374)
* [Video Youtube!](https://github.com/telegraph/clarity-youtube-pipeline/tree/DT-4336)
* [Dim Sprk Urls!](https://github.com/telegraph/clarity-dim-spark-campaigns-urls-pipeline/tree/DT-4359)

