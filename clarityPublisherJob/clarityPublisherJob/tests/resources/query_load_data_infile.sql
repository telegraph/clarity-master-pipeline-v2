LOAD DATA LOCAL infile '/path/to/local/file'
REPLACE
INTO TABLE test_schema.test_table
CHARACTER SET 'utf8mb4'
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '\"'
ESCAPED BY '\"'
(@id, @firstname, @lastname, @address, @date_of_birth)
SET
`id` = nullif(@id, ''),
`firstname` = nullif(@firstname, ''),
`lastname` = nullif(@lastname, ''),
`address` = nullif(@address, ''),
`date_of_birth` = nullif(@date_of_birth, '')
;
