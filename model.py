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

    def __init__(self, aid: str, site_name: str, pub_date: str, author: str, title: str, subtitle: str, aurl: str, atype: str = None, hat: str = None, mod_date: str = None):
        self.article_id = aid
        self.site_name = site_name
        self.published = pub_date
        self.author = author
        self.title = title
        self.subtitle = subtitle
        self.article_url = aurl
        self.article_type = atype
        self.hat = hat
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
            values[9]
        )

    @staticmethod
    def attr_list():
        """Retorna uma lista com os nomes dos atributos (campos) do objeto `Article``."""
        return list(Article('', '', '', '', '', '', '', '').__dict__)[:]

    def __str__(self):
        list_str = [f'{self.__class__.__name__}']
        for attr in self.attr_list():
            list_str.append(f'{attr}: {getattr(self, attr)}')
        return '\n'.join(list_str)


class ArticleImage(ModelEntity):

    def __init__(self, aid: str, src: str, order: int, height: int, width: int, img_type: str):
        self.article_id = aid
        self.img_src = src
        self.img_order = order
        self.img_height = height
        self.img_width = width
        self.img_type = img_type

    def to_tuple(self):
        """Retorna o objeto `ArticleImage` numa tupla."""
        return tuple(getattr(self, attr) for attr in self.attr_list())

    @classmethod
    def from_tuple(cls, values: Tuple):
        return ArticleImage(
            values[0],
            values[1],
            values[2],
            values[3],
            values[4],
            values[5]
        )

    @staticmethod
    def attr_list():
        """Retorna uma lista com os nomes dos atributos (campos) do objeto `ArticleImage``."""
        return list(ArticleImage('', '', -1, -1, -1, '').__dict__)[:]

    def __str__(self):
        list_str = [f'{self.__class__.__name__}']
        for attr in self.attr_list():
            list_str.append(f'{attr}: {getattr(self, attr)}')
        return '\n'.join(list_str)


class ArticleTopic(ModelEntity):

    def __init__(self, aid: str, desc: str, url: str, order: int):
        self.article_id = aid
        self.topic_description = desc
        self.topic_url = url
        self.topic_order = order

    def to_tuple(self):
        """Retorna o objeto `ArticleTopic` numa tupla."""
        return tuple(getattr(self, attr) for attr in self.attr_list())

    @classmethod
    def from_tuple(cls, values: Tuple):
        return ArticleTopic(
            values[0],
            values[1],
            values[2],
            values[3]
        )

    @staticmethod
    def attr_list():
        """Retorna uma lista com os nomes dos atributos (campos) do objeto `ArticleTopic`."""
        return list(ArticleTopic('', '', '', -1).__dict__)[:]

    def __str__(self):
        list_str = [f'{self.__class__.__name__}']
        for attr in self.attr_list():
            list_str.append(f'{attr}: {getattr(self, attr)}')
        return '\n'.join(list_str)


class ArticleMedia(ModelEntity):

    def __init__(self, aid: str, order: int, media_type: str, source: str):
        self.article_id = aid
        self.media_order = order
        self.media_type = media_type
        self.media_source = source

    def to_tuple(self):
        """Retorna o objeto `ArticleMedia` numa tupla."""
        return tuple(getattr(self, attr) for attr in self.attr_list())

    @classmethod
    def from_tuple(cls, values: Tuple):
        return ArticleMedia(
            values[0],
            values[1],
            values[2],
            values[3]
        )

    @staticmethod
    def attr_list():
        """Retorna uma lista com os nomes dos atributos (campos) do objeto `ArticleMedia``."""
        return list(ArticleMedia('', -1, '', '').__dict__)[:]

    def __str__(self):
        list_str = [f'{self.__class__.__name__}']
        for attr in self.attr_list():
            list_str.append(f'{attr}: {getattr(self, attr)}')
        return '\n'.join(list_str)


class ArticleHyperlink(ModelEntity):

    def __init__(self, aid: str, order: int, description: str, href: str):
        self.article_id = aid
        self.link_order = order
        self.link_description = description
        self.href = href

    def to_tuple(self):
        """Retorna o objeto `ArticleHyperlink` numa tupla."""
        return tuple(getattr(self, attr) for attr in self.attr_list())

    @classmethod
    def from_tuple(cls, values: Tuple):
        return ArticleHyperlink(
            values[0],
            values[1],
            values[2],
            values[3]
        )

    @staticmethod
    def attr_list():
        """Retorna uma lista com os nomes dos atributos (campos) do objeto `ArticleHyperlink``."""
        return list(ArticleHyperlink('', -1, '', '').__dict__)[:]

    def __str__(self):
        list_str = [f'{self.__class__.__name__}']
        for attr in self.attr_list():
            list_str.append(f'{attr}: {getattr(self, attr)}')
        return '\n'.join(list_str)


class ArticleCategory(ModelEntity):

    def __init__(self, aid: str, desc: str, href: str):
        self.article_id = aid
        self.description = desc
        self.href = href

    def to_tuple(self):
        """Retorna o objeto `ArticleCategory` numa tupla."""
        return tuple(getattr(self, attr) for attr in self.attr_list())

    @classmethod
    def from_tuple(cls, values: Tuple):
        return ArticleCategory(
            values[0],
            values[1],
            values[2]
        )

    @staticmethod
    def attr_list():
        """Retorna uma lista com os nomes dos atributos (campos) do objeto `ArticleCategory``."""
        return list(ArticleCategory('', '', '').__dict__)[:]

    def __str__(self):
        list_str = [f'{self.__class__.__name__}']
        for attr in self.attr_list():
            list_str.append(f'{attr}: {getattr(self, attr)}')
        return '\n'.join(list_str)


class ArticleParser:

    ARTICLE_ID_PROPERTY = 'article_id'
    ARTICLE_SITENAME_PROPERTY = 'og:site_name'
    ARTICLE_PUBLISHED_PROPERTY = 'article:published_time'
    ARTICLE_AUTHOR_PROPERTY = 'article:author'
    ARTICLE_TITLE_PROPERTY = 'og:title'
    ARTICLE_DESCRIPTION_PROPERTY = 'og:description'
    ARTICLE_URL_PROPERTY = 'og:url'
    ARTICLE_TYPE_PROPERTY = 'og:type'
    ARTICLE_HAT_PROPERTY = 'hat'
    ARTICLE_MODIFIED_PROPERTY = 'article:modified_time'

    @classmethod
    def parse_article(cls, article_metadata: Dict):
        return Article(
            article_metadata.get(ArticleParser.ARTICLE_ID_PROPERTY, None),
            article_metadata.get(ArticleParser.ARTICLE_SITENAME_PROPERTY, None),
            article_metadata.get(ArticleParser.ARTICLE_PUBLISHED_PROPERTY, None),
            article_metadata.get(ArticleParser.ARTICLE_AUTHOR_PROPERTY, None),
            article_metadata.get(ArticleParser.ARTICLE_TITLE_PROPERTY, None),
            article_metadata.get(ArticleParser.ARTICLE_DESCRIPTION_PROPERTY, None),
            article_metadata.get(ArticleParser.ARTICLE_URL_PROPERTY, None),
            article_metadata.get(ArticleParser.ARTICLE_TYPE_PROPERTY, None),
            article_metadata.get(ArticleParser.ARTICLE_HAT_PROPERTY, None),
            article_metadata.get(ArticleParser.ARTICLE_MODIFIED_PROPERTY, None)
        )
