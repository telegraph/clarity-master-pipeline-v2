# clarity-master-pipeline-v2
Repository for Clarity v2 deployment to Airflow 

## Overview 
Clarity is a dashboard that houses advertising related data and metrics that we offer to our advertising clients so they can keep track on how their ads are performing on our media platforms. It currently collects and aggregates data from Telegraph.co.uk, Edions App, News App, Apple News and various video hosting platforms. This project contains the logic that runs clarity back end data pipelines.
The DAG is designed read a yml file and automatically pick up new tasks (pipelines) to run. 

! [DAG](/clarity_v2_dag.png?raw=true)

## Project Structure 
The project is separated into three main sections 
### DAGs
This houses the DAG that is run on ariflow (edit with caution)
> **Airflow** - This is the platform where the project is run. For more information see the tech document https://docs.google.com/document/d/1wtDsqWfdBqoRhQtSXFTMaEGhKyynrOfdoveSh8b0KWM/edit# 
> SDVFD

