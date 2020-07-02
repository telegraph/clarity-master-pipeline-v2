LOAD DATA LOCAL infile '{{ data_file_path }}'
REPLACE 
INTO TABLE {{ table_schema}}.{{table_name}}
CHARACTER SET 'utf8mb4'
FIELDS
	TERMINATED BY '\t'
	ESCAPED BY '\"'
IGNORE 1 LINES
(@field_1, @field_2, @field_3, @field_4, @field_5, @field_6, @field_7, @field_8, @field_9, @field_10, @field_11, @field_12, @field_13, @field_14, @field_15)
SET
`date` = IF(@field_1 = '', NOT NULL, @field_1),
campaign = IF(@field_2 = '', NOT NULL, @field_2),
platform = IF(@field_3 = '',NOT NULL, @field_3),
leaderboard_megabanner_clicks = IF(@field_4 = '',NOT NULL, @field_4),
mpu_clicks = IF(@field_5 = '', NOT NULL, @field_5), 
sky_clicks = IF(@field_6 = '', NOT NULL, @field_6),
interstitial_clicks = IF(@field_7 = '', NOT NULL, @field_7),
mobile_native_clicks = IF(@field_8 = '', NOT NULL, @field_8),
reskin_clicks = IF(@field_9 = '', NOT NULL, @field_9),
leaderboard_megabanner_impressions = IF(@field_10 = '', NOT NULL, @field_10),
mpu_impressions = IF(@field_11 = '', NOT NULL, @field_11),
sky_impressions = IF(@field_12 = '', NOT NULL, @field_12),
interstitial_impressions = IF(@field_13 = '', NOT NULL, @field_13),
mobile_native_impressions = IF(@field_14 = '', NOT NULL, @field_14),
reskin_impressions = IF(@field_15 = '', NOT NULL, @field_15)
;