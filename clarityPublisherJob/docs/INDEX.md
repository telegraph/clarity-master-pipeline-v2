SidPublisherJob Software design
===============================

SidPublisherJob (SPJ) is a cli tool written in python to perform a transfer of SID data from BQ to Mysql.
Instances of SPJ are scheduled daily through an Airflow dag, one Task for each BQ Table.
An instance of SPJ can be run locally as a standalone app, this requires a high speed internet connection since it involves copying data to local disk.

## What does it do?

There's no direct connector in GCP to move data directly between BigQuery and Mysql.
 
In order to perform this transfer, Google suggest to execute the following operations:

1. Fetch the data with a BQ Query.
2. Save the result in CSV format in a GCS bucket.
3. Use _CloudInstance_ `ImportApi`, to import the csv file(s) the MySQL DB.

We followed Google's guidelines for the first two steps and we implemented a custom solution to optimize the transfer and work around the restriction
of the `CloudInstance` API.

We added a final step, which checks that the BQ and MySql tables have the same row count.

## What data is migrated

Each day, __SID__ tasks run according to their schedule. The result of the run is an _insertion_ of new rows or an _update_ of existing rows in the target table. 
The number of rows to insert/update ranges from less than 100 (mostly for dictionary-like table) to hundreds of thousands.
Table sizes vary also with the biggest table having a size of near 200Million rows.

These numbers makes clear that it's not a smart move to simply full-refresh each table every day.
This applies to medium-sized tables also, as we do not want to overload the server and slow down other transfers.
There are cases when a full refresh is necessary: when the table is very small, and when the table has to be re-initialized.

This is why we implemented two strategies to perform the migration: 

1. **Full refresh** of mysql table (for initialization or reboot after fixes)
2. **Incremental** update/insert of new BQ data (expected normal execution )

We will discuss the algorithm of each strategy later.


## Table of Content

1. [Index](./INDEX.md)
2. [Terminology](./TERMINOLOGY.md)
3. [Application Flow](./APPLICATION_FLOW.md)
4. [Transfer Clients](./CLIENTS.md)
5. [Helpers](./HELPERS.md)
6. [Sanity Check](./SANITY_CHECK.md)
7. [Configuration](./CONFIGURATION.md)
