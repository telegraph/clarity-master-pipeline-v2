LOAD DATA LOCAL infile '{{ data_file_path }}'
REPLACE
INTO TABLE {{ table_schema}}.{{table_name}}
CHARACTER SET 'utf8mb4'
FIELDS TERMINATED BY '\t'
	ESCAPED BY '\"'
IGNORE 1 LINES
(campaign, campaign_name, traffic, start_date, end_date, include_urls, exclude_urls, channel, tags, ooyala_ids, youtube_ids, teads_ids, facebook_ids, twitter_ids, wayin_ids, dfp_order_ids, apple_ids, @digital_revenue, @total_revenue, campaign_kpi_type, campaign_business_unit, on_site_uu, social_uu, @competition_submissions_kpi, @on_site_video_views_kpi, @inread_video_views_kpi, @social_video_views_kpi)

SET
digital_revenue = IF(@digital_revenue = '', '', @digital_revenue),
total_revenue = IF(@total_revenue = '', '', @total_revenue),
competition_submissions_kpi = IF(@competition_submissions_kpi = '', 0, @competition_submissions_kpi),
on_site_video_views_kpi = IF(@on_site_video_views_kpi = '', 0, @on_site_video_views_kpi),
inread_video_views_kpi =  IF(@inread_video_views_kpi = '', 0, @inread_video_views_kpi),
social_video_views_kpi = IF(@social_video_views_kpi = '', 0, @social_video_views_kpi)
;
