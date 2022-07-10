CREATE TABLE IF NOT EXISTS article
(
    article_id character varying(20) NOT NULL,
    site_name text COLLATE pg_catalog."default" NOT NULL,
    published timestamp,
    editorial text COLLATE pg_catalog."default",
    author text COLLATE pg_catalog."default",
    title text COLLATE pg_catalog."default" NOT NULL,
    subtitle text COLLATE pg_catalog."default",
    content text COLLATE pg_catalog."default",
    article_url text COLLATE pg_catalog."default",
    article_type text COLLATE pg_catalog."default",
    header text COLLATE pg_catalog."default",
    tags text COLLATE pg_catalog."default",
    img_url text COLLATE pg_catalog."default",
    img_type character varying(14) COLLATE pg_catalog."default",
    modified timestamp,
    CONSTRAINT article_pkey PRIMARY KEY (article_id)
);