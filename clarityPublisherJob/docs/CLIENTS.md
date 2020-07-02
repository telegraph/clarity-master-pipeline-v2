Truncate Client
==============

As the name suggest, the `TruncateClient` performs a full refresh of the table.
 
During object initialization it initialise a `QueryRenderer` object and a `MySqlConnection`

Here is it's logic to perform the full refresh:

1. Using the BQClient it dumps the table into one or multiple _CSV_ files, depending on the size of the table itself.
2. Instantiate a `BlobManager` context which takes care to merge all the partial _CSVs_ into one singe _CSV_ file as well as delete all the files at the end of the execution
3. Download the _CSV_ file in a local temporary directory
4. Truncate the table
4. Using `QueryRenderer` renders the `LOAD DATA INFILE` query which is executed by the `MysqlConnection` with the result of a fully refreshed table.


Delta Client
============

The `DeltaClient` is used when we want to update the destination table with only the rows inserted or updated after a given
date expressed by the _cli_ argument `EXECUTIION_DATE`. 

During object initialization it initialise a `QueryRenderer` object and a `MySqlConnection`

Here is the logic explained

1. **Fetch the data**.  
   -  Using `MySqlConnection` fetch the fields of the destination table 
   -  Using `QueryRederer` the `EXECUTION_DATE` and the field list, it prepares the query to fetch the most recent data from the `raw table`  
   
       ```jinja2
        -- delta_direct.sql
        WITH LAST_VALUES AS (
            SELECT
                {{ table_key }},
                MAX({{ most_recent_identifier }}) AS MOST_RECENT
            FROM `{{ raw_table }}` RAW_TABLE
            WHERE
                1=1
                AND RAW_TABLE.PARTITION_FIELD_DATE >= date(TIMESTAMP('{{ date }}'))
            GROUP BY {{ table_key }}
        )
        SELECT
            {%- for col in columns_to_select %}
            RAW_TABLE.{{col }} as {{ col }}{{ "," if not loop.last }}
            {%- endfor %}
        FROM `{{ raw_table }}` RAW_TABLE
        INNER JOIN LAST_VALUES
        ON RAW_TABLE.{{ table_key }} = LAST_VALUES.{{ table_key }}
        AND {{ most_recent_identifier }} = LAST_VALUES.MOST_RECENT
        
        ``` 
   - Execute the query and save the result files in gcs.
2. Instantiate a `BlobManager` context which takes care to merge all the partial _CSVs_ into one singe _CSV_ file as well delete all the files at the end of the execution
3. Download the _CSV_ file in a local temporary directory
4. **Delta Table**  
   - Using `MySqlConnection` it create an **delta table**, which is an empty table on mysql `delta_database` with the same structure as the destination table with the exception of the virtual fields, if specified in the confguration.
   - Drop all the indexes in the **delta table**
   - Using `QueryRenderer` renders the `LOAD DATA INFILE` query which is executed by the `MysqlConnection`, with the result of filling the **delta table**
5. Using `MysqlConnection`, it executes the following `REPLACE` statement to **UPSERT** the delta data into the destination table  

    ```mysql-sql
    REPLACE INTO <destination_table_name> ( <column list> ) select <column list> from delta_table;
    ```

## Table of Content

1. [Index](./INDEX.md)
2. [Terminology](./TERMINOLOGY.md)
3. [Application Flow](./APPLICATION_FLOW.md)
4. [Transfer Clients](./CLIENTS.md)
5. [Helpers](./HELPERS.md)
6. [Sanity Check](./SANITY_CHECK.md)
7. [Configuration](./CONFIGURATION.md)
