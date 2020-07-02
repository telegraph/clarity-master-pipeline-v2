Configuration
=============

## Global
```yaml
logger:
  push_to_pubsub: false #enables logging on pubsub

pubsub:
  subscription_name: sid-consumer #deprecated


project: tmg-plat-dev #bq project name
```

### Mysql parameters 

Defines destination db and temporary db for delta location and credentials
```yaml
mysql:
  instance_name: nick-sid-dev
  database: sid
  tmp_mysql_schema: sid_tmp 
  host: sql-proxy-service.default.svc.cluster.local
  user: changeme
  password: changeme
```

### BigQuery configuration
```yaml
bq:
  dataset: sid_development_processing # main sid database of processing
  sanity_check_dataset: sid_development_processing # database where we want to save the sanity check
  sanity_check_table: publisher_status # name of the table where to save the discrepancy
  delta_dataset: sid_transfer_deltas # dataset where to save the delta result

```
### Google Storage Configration
```yaml
gcs:
  bucket: sid-mysql-job-storage-dev # where to save the csv files
  file_ending: .csv # file extension

```

#Transfers

There are 2 transfer config structure, one for the TruncateClient and one for the DeltaClient. They share a common part tho.


```yaml

transfers:
    <transfer_object>

```

### Type Truncate

```yaml
 dim_agent: #transfer name
    transfer:
      method: truncate #specify which method to use

    bq_table: dim_agent #name of bq source table
    mysql_table: dim_agent #name of mysql destination table

    table_indexes: # list of indexes to drop before and recreate after the data upload 
      - name: dim_agent_nkc #name of the index
        columns: source_id,flag_current,name #columns of the index

```

### Type Delta
```yaml
fact_subscription_event:
    transfer:
      method: delta
      fields_to_omit: #list of field on the source table we DON'T WANT to copy on the destination table
        - PARTITION_FIELD_DATE
        - OPERATION
        - PIPELINE_ORDER

      # Optional 
      # specify how we build the value to identify the most recent row on a table for table more complex
      # Default: PARTITION_FIELD_DATE 
      most_recent_identifier: "CAST(CONCAT(FORMAT_DATE('%Y%m%d', RAW_TABLE.PARTITION_FIELD_DATE), CAST(RAW_TABLE.PIPELINE_ORDER AS STRING)) AS INT64)" 

    bq_table: fact_subscription_event #name of bq source table
    bq_raw_table: raw_fact_subscription_event #name of bq raw table
    bq_key: sk_subscription_event # table sk name

    mysql_fields_to_drop: ['indexhash'] #indicates which fields onf the delta table we don't want to copy into the destination table (this is for generated fields)

    mysql_table: fact_subscription_event #name of mysql destination table

    table_indexes: # list of indexes to drop before and recreate after the data upload 
      - name: sk_subscription_event_UNIQUE #name of the index
        columns: sk_subscription_event #columns of the index

```
