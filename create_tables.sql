CREATE TABLE IF NOT EXISTS article
(
    article_id varchar(40) PRIMARY KEY NOT NULL,
    article_url text NOT NULL,
    site_name text NOT NULL,
    published timestamp,
    author text,
    title text NOT NULL,
    subtitle text,
    article_type text,
    hat text,
    modified timestamp
);

CREATE TABLE IF NOT EXISTS article_topic
(
    topic_url text PRIMARY KEY NOT NULL,
    article_url text NOT NULL,
    topic_description text NOT NULL,
    topic_order smallint NOT NULL,
    UNIQUE (topic_url, article_url),
    FOREIGN KEY (article_url) REFERENCES article(article_url)
);

CREATE TABLE IF NOT EXISTS article_media
(
    media_source text PRIMARY KEY NOT NULL,
    article_url text NOT NULL,
    media_order smallint NOT NULL,
    media_type text NOT NULL,
    UNIQUE (media_source, article_url),
    FOREIGN KEY (article_url) REFERENCES article(article_url)
);

CREATE TABLE IF NOT EXISTS article_hyperlink
(
    hyperlink_source text PRIMARY KEY NOT NULL,
    article_url text NOT NULL,
    link_order smallint NOT NULL,
    link_description text NOT NULL,
    UNIQUE (hyperlink_source, article_url),
    FOREIGN KEY (article_url) REFERENCES article(article_url)
);

CREATE TABLE IF NOT EXISTS article_comment
(
    comment_id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    article_url text NOT NULL,
    user_name text NOT NULL,
    comment text NOT NULL,
    published_date timestamp,
    FOREIGN KEY (article_url) REFERENCES article(article_url)
);

CREATE TABLE IF NOT EXISTS article_category
(
    category_source text PRIMARY KEY NOT NULL,
    article_url text NOT NULL,
    description text NOT NULL,
    UNIQUE (category_source, article_url),
    FOREIGN KEY (article_url) REFERENCES article(article_url)
);