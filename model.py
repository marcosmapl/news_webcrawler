# -*- coding: utf-8 -*-
from typing import Dict, Tuple


class ModelEntity:
    """Interface que especifica os métodos de uma Entidade do Modelo de dados necessita implementar"""

    def to_tuple(self):
        """Retorna os valores dos atributos (campos) da Entidade organizados numa tupla (row)"""
        pass

    @classmethod
    def from_tuple(cls, values: Tuple):
        """Retorna um novo objeto com os valores da tupla informada"""
        pass

    @staticmethod
    def attr_list():
        """Retorna uma lista com o nome de todos os atributos da Entidade"""
        pass


class Article(ModelEntity):

    def __init__(self, aid: str, site_name: str, pub_date: str, editorial: str, author: str, title: str, subtitle: str, content: str, aurl: str, atype: str = None, header: str = None, tags: str = None, img_url: str = None, img_type: str = None, mod_date: str = None):
        self.article_id = aid
        self.site_name = site_name
        self.published = pub_date
        self.editorial = editorial
        self.author = author
        self.title = title
        self.subtitle = subtitle
        self.content = content
        self.article_url = aurl
        self.article_type = atype
        self.header = header
        self.tags = tags
        self.img_url = img_url
        self.img_type = img_type
        self.modified = mod_date

    def to_tuple(self):
        """Retorna o objeto `Article` numa tupla."""
        return tuple(getattr(self, attr) for attr in self.attr_list())

    @classmethod
    def from_tuple(cls, values: Tuple):
        return Article(
            values[0],
            values[1],
            values[2],
            values[3],
            values[4],
            values[5],
            values[6],
            values[7],
            values[8],
            values[9],
            values[10],
            values[11]
        )

    @staticmethod
    def attr_list():
        """Retorna uma lista com os nomes dos atributos (campos) do objeto `Article``."""
        return list(Article('', '', '', '', '', '', '', '', '').__dict__)[:]

    def __str__(self):
        list_str = [f'{self.__class__.__name__}']
        for attr in self.attr_list():
            list_str.append(f'{attr}: {getattr(self, attr)}')
        return '\n'.join(list_str)


class AcriticaParser:

    __ARTICLE_ID_PROPERTY = 'article_id'
    __ARTICLE_SITENAME_PROPERTY = 'og:site_name'
    __ARTICLE_PUBLISHED_PROPERTY = 'article:published_time'
    __ARTICLE_EDITORIAL_PROPERTY = 'editorial'
    __ARTICLE_AUTHOR_PROPERTY = 'article:author'
    __ARTICLE_TITLE_PROPERTY = 'og:title'
    __ARTICLE_DESCRIPTION_PROPERTY = 'og:description'
    __ARTICLE_CONTENT_PROPERTY = 'content'
    __ARTICLE_URL_PROPERTY = 'og:url'
    __ARTICLE_TYPE_PROPERTY = 'og:type'
    __ARTICLE_HEADER_PROPERTY = 'header'
    __ARTICLE_TAGS_PROPERTY = 'tags'
    __ARTICLE_IMAGE_PROPERTY = 'og:image'
    __ARTICLE_IMGTYPE_PROPERTY = 'og:image:type'
    __ARTICLE_MODIFIED_PROPERTY = 'article:modified_time'

    @classmethod
    def parse_article(cls, article_metadata: Dict):
        return Article(
            article_metadata.get(AcriticaParser.__ARTICLE_ID_PROPERTY, None),
            article_metadata.get(AcriticaParser.__ARTICLE_SITENAME_PROPERTY, None),
            article_metadata.get(AcriticaParser.__ARTICLE_PUBLISHED_PROPERTY, None),
            article_metadata.get(AcriticaParser.__ARTICLE_EDITORIAL_PROPERTY, None),
            article_metadata.get(AcriticaParser.__ARTICLE_AUTHOR_PROPERTY, None),
            article_metadata.get(AcriticaParser.__ARTICLE_TITLE_PROPERTY, None),
            article_metadata.get(AcriticaParser.__ARTICLE_DESCRIPTION_PROPERTY, None),
            article_metadata.get(AcriticaParser.__ARTICLE_CONTENT_PROPERTY, None),
            article_metadata.get(AcriticaParser.__ARTICLE_URL_PROPERTY, None),
            article_metadata.get(AcriticaParser.__ARTICLE_TYPE_PROPERTY, None),
            article_metadata.get(AcriticaParser.__ARTICLE_HEADER_PROPERTY, None),
            article_metadata.get(AcriticaParser.__ARTICLE_TAGS_PROPERTY, None),
            article_metadata.get(AcriticaParser.__ARTICLE_IMAGE_PROPERTY, None),
            article_metadata.get(AcriticaParser.__ARTICLE_IMGTYPE_PROPERTY, None),
            article_metadata.get(AcriticaParser.__ARTICLE_MODIFIED_PROPERTY, None)
        )
