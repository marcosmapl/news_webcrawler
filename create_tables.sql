CREATE TABLE article (
	article_id int NOT NULL,
	site_name text NOT NULL,
	title text NOT NULL,
	description text,
	author text,
	url text,
	type text,
	category text,
	img_url text,
	img_type varchar(14),
	salesrank int,
	published date,
	modified date,
	PRIMARY KEY (article_id)
);
