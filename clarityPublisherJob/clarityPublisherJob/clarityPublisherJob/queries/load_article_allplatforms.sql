LOAD DATA LOCAL infile '{{ data_file_path }}'
REPLACE INTO TABLE article_allplatforms
CHARACTER SET 'utf8mb4'
FIELDS
	TERMINATED BY '\t'
	OPTIONALLY ENCLOSED BY '\"'
	ESCAPED BY '\"'
IGNORE 1 LINES