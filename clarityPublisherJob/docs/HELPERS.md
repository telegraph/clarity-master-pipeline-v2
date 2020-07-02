Helpers
=======

Under the category of helpers we put all the classes / services created with the purpose of executing simple tasks during the main logic of the transfer.

### BlobManager

The `BlobManager` class implemented with a context manager, serve the purpose of merging the data _CSVs_ files into a single one and leaving the environment clean at the end of the transfer.
During the context the actions of transferring the data to mysql are performed.

#### Blob Composer
The `BlobComposer` class is a small class that computes the instruction to merge multiple _CSV_ files into one.


### QueryRenderer

The `QueryRenderer` is a class that wraps a `JinjaEnvironment` and returns the correct rendered query according to the `TransferConfiguration` object passed during its construction.

### Traffic Light
Wrapper of python `Lock` class to avoid race condition during SQL calls. It was used on the previous implementation, Will be depreacted in the future releases.


## Table of Content

1. [Index](./INDEX.md)
2. [Terminology](./TERMINOLOGY.md)
3. [Application Flow](./APPLICATION_FLOW.md)
4. [Transfer Clients](./CLIENTS.md)
5. [Helpers](./HELPERS.md)
6. [Sanity Check](./SANITY_CHECK.md)
7. [Configuration](./CONFIGURATION.md)
