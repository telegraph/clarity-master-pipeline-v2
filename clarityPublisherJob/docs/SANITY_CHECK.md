Sanity Check
============

The `SanityCheck` Service performs a comparison of number of rows between the _BQ source table_ and _Mysql table_ and
return the difference.
When the transfer is successful a difference of 1 is expected as the destination table will always contain the header row.
When the difference is positive it means that `MySQL` has more row that `BQ` suggesting the `MySql table` is outdated


## Table of Content

1. [Index](./INDEX.md)
2. [Terminology](./TERMINOLOGY.md)
3. [Application Flow](./APPLICATION_FLOW.md)
4. [Transfer Clients](./CLIENTS.md)
5. [Helpers](./HELPERS.md)
6. [Sanity Check](./SANITY_CHECK.md)
7. [Configuration](./CONFIGURATION.md)
