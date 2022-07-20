# -*- coding: utf-8 -*-
import os
import re
from time import sleep
from typing import List

from bs4 import BeautifulSoup
from bs4.element import Comment
from selenium import webdriver

from database import ArticleController, ArticleTopicController, ArticleHyperlinkController, ArticleCategoryController, ArticleMediaController
from logs import Logger
from model import ArticleParser, ArticleTopic, ArticleMedia, ArticleHyperlink, ArticleCategory, Article


class WebScraper:

    def __init__(self):
        self._BASE_URL = 'https://'
        self._LOAD_WAITING_TIME = 3
        self._OUTPUT_DIR = 'scrapper'
        self._NAME = 'Scrapper'

    def _get_document_links(self, search_term: str, browser):
        return set()

    def _get_document(self, document_url: str, browser):
        pass

    def start(self, search_terms: List[str]):
        self._create_output_dirs()
        Logger.info(f"[{self.get_scrapper_name()}]: INICIANDO O WEBDRIVER")
        browser = webdriver.Chrome()
        browser.maximize_window()

        document_links = set()
        for term in search_terms:
            document_links.update(self._get_document_links(term, browser))

        for document_link in document_links:
            try:
                self._get_document(document_link, browser)
            except Exception as err:
                Logger.error(str(err))

        Logger.info(f"[{self.get_scrapper_name()}]: ENCERRANDO O WEBDRIVER")
        browser.get(r'https://www.google.com.br')
        browser.close()
        browser.quit()

    def get_scrapper_name(self):
        return self._NAME

    def get_base_url(self):
        return self._BASE_URL

    def get_output_dir(self):
        return self._OUTPUT_DIR

    def get_load_waiting_time(self):
        return self._LOAD_WAITING_TIME

    def _get_article_metadata(self, soup):
        return {meta['property']: str(meta['content']).upper().strip() for meta in soup.findAll('meta', {'property': True})}

    def _get_article_topics(self, soup, article_id):
        Logger.info(f"[{self.get_scrapper_name()}]: OBTENDO TOPICOS DO DOCUMENTO {article_id}")
        topics = []
        if soup:
            for order, link in enumerate(soup, start=1):
                topics.append(
                    ArticleTopic(
                        -1,
                        article_id,
                        link.text.strip().upper(),
                        link['href'],
                        order
                    )
                )
        return topics

    def _get_article_hyperlinks(self, soup, article_id: int):
        Logger.info(f"[{self.get_scrapper_name()}]: OBTENDO HYPERLINKS DO DOCUMENTO {article_id}")
        hyperlinks = []
        if soup:
            for order, link in enumerate(soup, start=1):
                hyperlinks.append(
                    ArticleHyperlink(
                        -1,
                        article_id,
                        order,
                        link.text.strip().upper(),
                        link['href']
                    )
                )
        return hyperlinks

    def _get_article_categories(self, soup, article_id: int):
        Logger.info(f"[{self.get_scrapper_name()}]: OBTENDO CATEGORIAS DO DOCUMENTO {article_id}")
        categories = []
        if soup:
            for order, link in enumerate(soup, start=1):
                categories.append(
                    ArticleCategory(
                        -1,
                        article_id,
                        link.text.strip().upper(),
                        link['href']
                    )
                )
        return categories

    def _get_document_medias(self, soup, article_id: int):
        Logger.info(f"[{self.get_scrapper_name()}]: OBTENDO MIDIAS DO DOCUMENTO {article_id}")
        medias = []
        for media_tag in ['video', 'audio', 'img']:
            for order, tag in enumerate(soup.findChildren(media_tag, {'src': True}), start=1):
                medias.append(
                    ArticleMedia(
                        -1,
                        article_id,
                        order,
                        media_tag.upper(),
                        tag['src']
                    )
                )
        for order, video_embed_div in enumerate(soup.findChildren('div', {'class': 'video-embed-wrapper'}), start=1):
            video_iframe = video_embed_div.findChild('iframe', {'src': True})
            medias.append(
                ArticleMedia(
                    -1,
                    article_id,
                    order,
                    'YOUTUBE/VIDEO',
                    video_iframe['src']
                )
            )

        return medias

    def _tag_visible(self, element):
        if element.parent.name in [
            'style', 'script', 'head', 'title', 'meta', '[document]'
        ]:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def _save_html(self, article_id: str, html: str):
        self._save_document_to_file(
            os.path.join(
                os.getcwd(),
                self.get_output_dir(),
                'html',
                f"{article_id}.html"
            ),
            html
        )

    def _save_txt(self, article_id: str, txt: str):
        self._save_document_to_file(
            os.path.join(
                os.getcwd(),
                self.get_output_dir(),
                'txt',
                f"{article_id}.txt"
            ),
            txt
        )

    def _save_document_to_file(self, file_path: str, text: str):
        Logger.info(f"[{self.get_scrapper_name()}]: SALVANDO DOCUMENTO {file_path}")
        with open(file_path, 'w', encoding='utf-8') as arq:
            arq.write(text)

    def _create_output_dirs(self):
        Logger.info(f"[{self.get_scrapper_name()}]: CRIANDO OS DIRETORIOS DE SAIDA")
        if not os.path.isdir(os.path.join(os.getcwd(), self.get_output_dir(), 'html')):
            os.makedirs(os.path.join(os.getcwd(), self.get_output_dir(), 'html'))
        if not os.path.isdir(os.path.join(os.getcwd(), self.get_output_dir(), 'txt')):
            os.makedirs(os.path.join(os.getcwd(), self.get_output_dir(), 'txt'))


class AcriticaScraper(WebScraper):

    def __init__(self, output: str, load_wait: int = None):
        WebScraper.__init__(self)
        self._BASE_URL = r'https://www.acritica.com'
        self._OUTPUT_DIR_NAME = output
        self._NAME = 'AcriticaScraper'
        if load_wait:
            self._DEFAULT_LOAD_WAITING_TIME = load_wait

    def _get_document_links(self, search_term: str, browser):
        document_links = set()
        Logger.info(f'[{self.get_scrapper_name()}]: OBTENDO DOCUMENTOS COM O TERMO "{search_term}" ')
        i = 1
        while True:
            browser.get(f'{self.get_base_url()}/page/{i}/{search_term}')
            sleep(self.get_load_waiting_time())
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            div_article_list = soup.find('div', {'class': 'bwIhbp'})
            links = div_article_list.findChildren('a', {'class': 'dDfqGJ', 'href': True})
            if links:
                i += 1
                for link in links:
                    document_links.add(link['href'])
                    Logger.info(f"[{self.get_scrapper_name()}]: DOCUMENTO ENCONTRADO E ADICIONADO A LISTA DE DOWNLOAD: {link['href']}")
            else:
                break
        return document_links

    def _get_article_metadata(self, soup):
        article_metadata = WebScraper._get_article_metadata(self, soup)
        article_metadata[ArticleParser.ARTICLE_ID_PROPERTY] = None
        article_metadata[ArticleParser.ARTICLE_CODE_PROPERTY] = 'AC' + article_metadata['og:url'][article_metadata['og:url'].rindex('.') + 1:]
        hat_span = soup.find('span', {'class': 'ceiOww'})
        article_metadata[ArticleParser.ARTICLE_HAT_PROPERTY] = hat_span.text.upper().strip() if hat_span else None

        div_content = soup.find('div', {'class': 'gzQsJ'})
        text_list = []
        contents = div_content.findChildren()
        for content in contents:
            if content.text and content.text not in text_list:
                text_list.append(content.text)
        article_metadata['content'] = '\n'.join([str(x).strip().upper() for x in text_list])

        return article_metadata

    def _get_document(self, document_url: str, browser):
        document_url = f'{self.get_base_url()}{document_url}'
        Logger.info(f'[{self.get_scrapper_name()}]: COLETANDO DOCUMENTO: {document_url}')
        browser.get(document_url)
        sleep(self.get_load_waiting_time())
        soup = BeautifulSoup(browser.page_source, 'html.parser')

        article_metadata = self._get_article_metadata(soup)
        article = ArticleParser.parse_article(article_metadata)

        ArticleController.insert_one(article)
        article_row = ArticleController.fetch_by_text_field(article.article_url, 'article_url')
        article = Article.from_tuple(article_row[0])
        WebScraper._save_html(self, f'{article.article_code}_{article.article_id}', soup.prettify())
        WebScraper._save_txt(self, f'{article.article_code}_{article.article_id}', re.sub(r"\s+", " ", ''.join(article_metadata['content']).upper()))

        div_content = soup.find('div', {'class': 'gzQsJ'})

        topics = WebScraper._get_article_topics(self, div_content.findChildren('a', {'class': 'knlcwJ', 'href': True}), article.article_id)
        for topic in topics:
            ArticleTopicController.insert_one(topic)

        hyperlinks = WebScraper._get_article_hyperlinks(self, div_content.findChildren('a', {'href': True}), article.article_id)
        for hyperlink in hyperlinks:
            ArticleHyperlinkController.insert_one(hyperlink)

        categories = self._get_article_categories(soup, article.article_id)
        for category in categories:
            ArticleCategoryController.insert_one(category)

        medias = WebScraper._get_document_medias(self, div_content, article.article_id)
        for media in medias:
            ArticleMediaController.insert_one(media)

    def _get_article_categories(self, soup, article_id):
        Logger.info(f'[{self.get_scrapper_name()}]: OBTENDO CATEGORIAS DO DOCUMENTO {article_id}')
        meta_url = soup.find('meta', {'property': 'og:url', 'content': True})
        document_url = meta_url['content']
        document_url = document_url.replace(self.get_base_url(), '')
        categories = []
        cat_paths = document_url.split('/')
        if cat_paths and len(cat_paths) > 2:
            for order, path in enumerate(cat_paths[1:-1], start=1):
                categories.append(
                    ArticleCategory(
                        -1,
                        article_id,
                        path.strip().upper(),
                        f'/{path}'
                    )
                )
        return categories


class PortalAmazoniaScraper(WebScraper):

    def __init__(self, output: str, load_wait: int = None):
        WebScraper.__init__(self)
        self._BASE_URL = r'https://portalamazonia.com'
        self._OUTPUT_DIR_NAME = output
        self._NAME = 'PortalAmazoniaScraper'
        if load_wait:
            self._DEFAULT_LOAD_WAITING_TIME = load_wait

    def _get_article_metadata(self, soup):
        article_metadata = WebScraper._get_article_metadata(self, soup)
        article_metadata[ArticleParser.ARTICLE_ID_PROPERTY] = None

        div_id = soup.find('div', {'data-id': True})
        article_metadata[ArticleParser.ARTICLE_CODE_PROPERTY] = 'PAM' + div_id['data-id']

        span_author = div_id.findChild('span', {'class': 'eb-meta-author', 'itemprop': 'author'})
        article_metadata[ArticleParser.ARTICLE_AUTHOR_PROPERTY] = span_author.text.upper().strip() if span_author else None

        article_metadata[ArticleParser.ARTICLE_PUBLISHED_PROPERTY] = soup.find('time', {'itemprop': 'datePublished'}).text.strip()
        article_metadata[ArticleParser.ARTICLE_MODIFIED_PROPERTY] = soup.find('time', {'itemprop': 'dateModified'}).text.strip()

        article_metadata['content'] = div_id.text.upper()
        return article_metadata

    def _get_document_links(self, search_term: str, browser):
        article_links = set()
        Logger.info(f'[{self.get_scrapper_name()}]: OBTENDO DOCUMENTOS COM O TERMO "{search_term}"')
        browser.get(f'{self.get_base_url()}/busca?q={search_term}')
        sleep(self.get_load_waiting_time())
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        for div_item in soup.find_all('div', {'class': 'result-item'}):
            article_links.add(div_item.findChild('a', {'href': True})['href'])

        if soup.find('ul', {'class': 'pagination'}):
            page = 1
            while True:
                browser.get(f'{self.get_base_url()}/busca?q={search_term}&start={page*20}')
                sleep(self.get_load_waiting_time())
                soup = BeautifulSoup(browser.page_source, 'html.parser')
                items = soup.find_all('div', {'class': 'result-item'})
                if not items:
                    break
                for item in items:
                    article_links.add(item.findChild('a', {'href': True})['href'])
                page += 1
        return article_links

    def _get_document(self, document_url: str, browser):
        document_url = f'{self.get_base_url()}{document_url}'
        Logger.info(f'[{self.get_scrapper_name()}]: COLETANDO DOCUMENTO: {document_url}')
        browser.get(document_url)
        sleep(self.get_load_waiting_time())
        soup = BeautifulSoup(browser.page_source, 'html.parser')

        article_metadata = self._get_article_metadata(soup)
        article = ArticleParser.parse_article(article_metadata)
        ArticleController.insert_one(article)
        article_row = ArticleController.fetch_by_text_field(article.article_url, 'article_url')
        article = Article.from_tuple(article_row[0])
        WebScraper._save_html(self, f'{article.article_code}_{article.article_id}', soup.prettify())
        WebScraper._save_txt(self, f'{article.article_code}_{article.article_id}', re.sub(r"\s+", " ", ''.join(article_metadata['content']).upper()))

        div_content = soup.find('div', {'id': True, 'class': 'eb-entry', 'data-id': True, 'data-uid': True})

        cell_tags = div_content.find('div', {'class': 'cell-tags'})
        topics = WebScraper._get_article_topics(self, cell_tags.findChildren('a', {'href': True}) if cell_tags else None, article.article_id)
        for topic in topics:
            ArticleTopicController.insert_one(topic)

        hyperlinks = WebScraper._get_article_hyperlinks(self, div_content.findChildren('a', {'href': True}), article.article_id)
        for hyperlink in hyperlinks:
            ArticleHyperlinkController.insert_one(hyperlink)

        div_categories = soup.findChild('div', {'class': 'eb-meta-category'})
        categories = WebScraper._get_article_categories(self, div_categories.findChildren('a', {'href': True}), article.article_id)
        for category in categories:
            ArticleCategoryController.insert_one(category)

        medias = WebScraper._get_document_medias(self, div_content, article.article_id)
        for media in medias:
            ArticleMediaController.insert_one(media)
