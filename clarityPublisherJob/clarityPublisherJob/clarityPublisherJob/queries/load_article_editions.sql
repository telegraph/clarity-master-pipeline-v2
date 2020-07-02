LOAD DATA LOCAL infile '{{ data_file_path }}'
REPLACE INTO TABLE article_editions
CHARACTER SET 'utf8mb4'
FIELDS
	TERMINATED BY '\t'
	ESCAPED BY '\"'
IGNORE 1 LINES