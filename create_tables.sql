CREATE TABLE IF NOT EXISTS article
(
    article_id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    article_code character varying(20) NOT NULL,
    site_name text NOT NULL,
    published timestamp,
    author text,
    title text NOT NULL,
    subtitle text,
    article_url text NOT NULL UNIQUE,
    article_type text,
    hat text,
    modified timestamp
);

CREATE TABLE IF NOT EXISTS article_topic
(
    topic_id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    article_id integer NOT NULL,
    topic_url text NOT NULL,
    topic_description text NOT NULL,
    topic_order smallint NOT NULL,
    UNIQUE (article_id, topic_url),
    FOREIGN KEY (article_id) REFERENCES article(article_id)
);

CREATE TABLE IF NOT EXISTS article_media
(
    media_id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    article_id integer NOT NULL,
    media_order smallint NOT NULL,
    media_type text NOT NULL,
    media_source text NOT NULL,
    UNIQUE (article_id, media_source),
    FOREIGN KEY (article_id) REFERENCES article(article_id)
);

CREATE TABLE IF NOT EXISTS article_hyperlink
(
    hyperlink_id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    article_id integer NOT NULL,
    link_order smallint NOT NULL,
    link_description text NOT NULL,
    href text NOT NULL,
    UNIQUE (article_id, href),
    FOREIGN KEY (article_id) REFERENCES article(article_id)
);

CREATE TABLE IF NOT EXISTS article_category
(
    category_id integer PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    article_id integer NOT NULL,
    description text NOT NULL,
    href text NOT NULL,
    UNIQUE (article_id, href),
    FOREIGN KEY (article_id) REFERENCES article(article_id)
);