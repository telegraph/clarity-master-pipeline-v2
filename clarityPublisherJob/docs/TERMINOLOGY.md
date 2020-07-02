Terminology
============

We design the full logic modeling each part of the application in separated modules, trying to follow S.O.L.I.D principles and clean code at best.
There is, of course, room for improvements. 

Here is a brief description of the entities we defined and implemented in our application.

#### \<Something\>Configuration

A plain data object modeling a piece of configuration.

#### Transfer

The `Transfer` is an action that expresses a migration of data between a BQ source table and a Mysql Destination Table.

The `Transfer` is implemented by a superclass `TransferClient` and the concrete classes `TruncateClient` and `DeltaDirectClient`

The `Transfer` is configured by `TransferConfiguration`, a simple data object populated by main routine according to the content of the configuration file.

### Transfer Method or Strategy

The transfer method is a property of the configuration that dictates which strategy we want use to migrate the data.

#### Blob
Identifies a gcs object

#### BlobManager
A service that merge multiple blobs (each one containing part of the data) into a single blob.
Implemented with a python context manager which clean the files at the end of its life, leaving the GCS bucket clean.

#### Query Renderer
Small helper class that renders query jinja into strings.

#### Sanity Check
The action of checking that BQ and MySQL table have the same size.


## Table of Content

1. [Index](./INDEX.md)
2. [Terminology](./TERMINOLOGY.md)
3. [Application Flow](./APPLICATION_FLOW.md)
4. [Transfer Clients](./CLIENTS.md)
5. [Helpers](./HELPERS.md)
6. [Sanity Check](./SANITY_CHECK.md)
7. [Configuration](./CONFIGURATION.md)
