# -*- coding: utf-8 -*-
from typing import Dict


class ModelEntity:
    """Interface que especifica os métodos de uma Entidade do Modelo de dados necessita implementar"""

    def to_tuple(self):
        """Retorna os valores dos atributos (campos) da Entidade organizados numa tupla (row)"""
        pass

    @staticmethod
    def attr_list():
        """Retorna uma lista com o nome de todos os atributos da Entidade"""
        pass


class Article(ModelEntity):

    def __init__(self, site_name: str, title: str, desc: str, author: str, url: str, type: str, cat: str = None, img_url: str = None, img_type: str = None, pub: str = None, mod: str = None):
        self.site_name = site_name
        self.title = title
        self.description = desc
        self.author = author
        self.url = url
        self.type = type
        self.category = cat
        self.img_url = img_url
        self.img_type = img_type
        self.published = pub
        self.modified = mod

    def to_tuple(self):
        """Retorna o objeto `Article` numa tupla."""
        values = []
        for attr in self.attr_list():
            values.append(getattr(self, attr))
        return tuple(values)

    @staticmethod
    def attr_list():
        """Retorna uma lista com os nomes dos atributos (campos) do objeto `Article``."""
        return list(Article('', '', '', '', '', '').__dict__)[:]

    def __str__(self):
        list_str = [f'{self.__class__.__name__}']
        for attr in self.attr_list():
            list_str.append(f'{attr}: {getattr(self, attr)}')
        return '\n'.join(list_str)


class AcriticaParser:

    __ARTICLE_SITENAME_PROPERTY = 'og:site_name'
    __ARTICLE_TITLE_PROPERTY = 'og:title'
    __ARTICLE_DESCRIPTION_PROPERTY = 'og:description'
    __ARTICLE_AUTHOR_PROPERTY = 'article:author'
    __ARTICLE_URL_PROPERTY = 'og:url'
    __ARTICLE_TYPE_PROPERTY = 'og:type'
    __ARTICLE_CATEGORY_PROPERTY = 'og:category'
    __ARTICLE_IMAGE_PROPERTY = 'og:image'
    __ARTICLE_IMGTYPE_PROPERTY = 'og:image:type'
    __ARTICLE_PUBLISHED_PROPERTY = 'article:published_time'
    __ARTICLE_MODIFIED_PROPERTY = 'article:modified_time'

    @classmethod
    def parse_article(cls, article_metadata: Dict):
        return Article(
            article_metadata.get(AcriticaParser.__ARTICLE_SITENAME_PROPERTY, None),
            article_metadata.get(AcriticaParser.__ARTICLE_TITLE_PROPERTY, None),
            article_metadata.get(AcriticaParser.__ARTICLE_DESCRIPTION_PROPERTY, None),
            article_metadata.get(AcriticaParser.__ARTICLE_AUTHOR_PROPERTY, None),
            article_metadata.get(AcriticaParser.__ARTICLE_URL_PROPERTY, None),
            article_metadata.get(AcriticaParser.__ARTICLE_TYPE_PROPERTY, None),
            article_metadata.get(AcriticaParser.__ARTICLE_CATEGORY_PROPERTY, None),
            article_metadata.get(AcriticaParser.__ARTICLE_IMAGE_PROPERTY, None),
            article_metadata.get(AcriticaParser.__ARTICLE_IMGTYPE_PROPERTY, None),
            article_metadata.get(AcriticaParser.__ARTICLE_PUBLISHED_PROPERTY, None),
            article_metadata.get(AcriticaParser.__ARTICLE_MODIFIED_PROPERTY, None)
        )
