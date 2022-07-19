CREATE TABLE IF NOT EXISTS article
(
    article_id character varying(20) NOT NULL,
    site_name text NOT NULL,
    published timestamp,
    author text,
    title text NOT NULL,
    subtitle text,
    article_url text,
    article_type text,
    hat text,
    modified timestamp,
    CONSTRAINT article_pkey PRIMARY KEY (article_id)
);

CREATE TABLE IF NOT EXISTS article_image
(
    article_id character varying(20) NOT NULL,
    img_src text NOT NULL,
    img_order smallint,
    img_height smallint,
    img_width smallint,
    img_type character varying(14),
    PRIMARY KEY (article_id, img_src),
    FOREIGN KEY (article_id) REFERENCES article(article_id)
);


CREATE TABLE IF NOT EXISTS article_topic
(
    article_id character varying(20) NOT NULL,
    topic_description text NOT NULL,
    topic_url text NOT NULL,
    topic_order smallint NOT NULL,
    PRIMARY KEY (article_id, topic_url),
    FOREIGN KEY (article_id) REFERENCES article(article_id)
);

CREATE TABLE IF NOT EXISTS article_media
(
    article_id character varying(20) NOT NULL,
    media_order smallint NOT NULL,
    media_type text NOT NULL,
    media_source text NOT NULL,
    PRIMARY KEY (article_id, media_source),
    FOREIGN KEY (article_id) REFERENCES article(article_id)
);

CREATE TABLE IF NOT EXISTS article_hyperlink
(
    article_id character varying(20) NOT NULL,
    link_order smallint NOT NULL,
    link_description text NOT NULL,
    href text NOT NULL,
    PRIMARY KEY (article_id, href),
    FOREIGN KEY (article_id) REFERENCES article(article_id)
);

CREATE TABLE IF NOT EXISTS article_category
(
    article_id character varying(20) NOT NULL,
    description text NOT NULL,
    href text NOT NULL,
    PRIMARY KEY (article_id, href),
    FOREIGN KEY (article_id) REFERENCES article(article_id)
);