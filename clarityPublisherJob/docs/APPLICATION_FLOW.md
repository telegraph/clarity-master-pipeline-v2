Application Flow
================

The application is a command-line tool build using the [Click](https://click.palletsprojects.com/en/7.x/) library.

### Command line interface 

From version `2.1.4`

```bash
pipeline [OPTIONS] EXECUTION_DATE TRANSFER_NAME CONFIG_LOCATION
```

- `EXECUTION_DATE`: the day of execution - used to filter the data we want to copy (ignored in full-refresh)
- `TRANSFER_NAME`: the transfer we want to execute
- `CONFIG_LOCATION`: the location of the configuration yml file. It can be a local yml file or a gcs path

`OPTIONS` are 
```bash
--full-refresh
```

- `full-refresh` is a flag that override the configuration and perform a full refresh of the table with the latest data available.

### Main Application logic.

The following operations are executed from the application once is launched from the command line.

1. Download or read directly the configuration file.
2. Build the `ApplicationConfig` object which contains the configuration for all the transfers. During the parsing of the config, an error is thrown if it does match the expected structure.
3. Retrieve the `TransferConfiguration` object which correspond to the `TRANSFER_NAME`
4. Create an instance of the application-wide BigQuery connector
4. Instantiate the appropriate TransferClient subclass according to the `TransferConfig` property
5. Run the transfer client
6. Perform the Sanity Check


## Table of Content

1. [Index](./INDEX.md)
2. [Terminology](./TERMINOLOGY.md)
3. [Application Flow](./APPLICATION_FLOW.md)
4. [Transfer Clients](./CLIENTS.md)
5. [Helpers](./HELPERS.md)
6. [Sanity Check](./SANITY_CHECK.md)
7. [Configuration](./CONFIGURATION.md)
