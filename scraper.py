# -*- coding: utf-8 -*-
import os
import re
import urllib.parse
from datetime import datetime
from time import sleep
from typing import List

from bs4 import BeautifulSoup
from bs4.element import Comment
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from database import ArticleController, ArticleTopicController, ArticleHyperlinkController, ArticleCategoryController, \
    ArticleMediaController
from logs import Logger
from model import ArticleParser, ArticleTopic, ArticleMedia, ArticleHyperlink, ArticleCategory, Article


class WebScraper:

    def __init__(self, wait_time: int, from_timestamp: float, to_timestamp: float, save_html: bool, save_txt: bool, save_db: bool):
        self._NAME = 'Scrapper'
        self._BASE_URL = 'https://'
        self._OUTPUT_DIR_NAME = 'news_output'
        self._LOAD_WAITING_TIME = wait_time
        self._FROM_TIMESTAMP = from_timestamp
        self._TO_TIMESTAMP = to_timestamp
        self._SAVE_HTML = save_html
        self._SAVE_TXT = save_txt
        self._SAVE_DB = save_db

    def _get_document_links(self, browser, search_term: str):
        return set()

    def _get_document(self, browser, page_url: str):
        pass

    def start(self, search_terms: List[str]):
        Logger.info(f"[{self.get_scrapper_name()}]: STARTED")
        op = webdriver.ChromeOptions()
        # op.add_argument('headless')
        browser = webdriver.Chrome(ChromeDriverManager().install(), options=op)
        browser.maximize_window()

        page_urls = set()
        for term in search_terms:
            page_urls.update(self._get_document_links(browser, term))

        for page_url in page_urls:
            try:
                self._get_document(browser, page_url)
            except Exception as err:
                Logger.error(str(err))

        Logger.info(f"[{self.get_scrapper_name()}]: FINISHED")
        browser.get(r'https://www.google.com.br')
        browser.close()
        browser.quit()

    def get_scrapper_name(self):
        return self._NAME

    def get_base_url(self):
        return self._BASE_URL

    def get_output_dir(self):
        return self._OUTPUT_DIR_NAME

    def get_load_waiting_time(self):
        return self._LOAD_WAITING_TIME

    def _get_article_metadata(self, soup):
        Logger.info(f"\tGETTING ARTICLE METADATA")
        return {meta['property']: str(meta['content']).upper().strip() for meta in
                soup.findAll('meta', {'property': True})}

    def _get_article_topics(self, soup, article_url: str):
        Logger.info(f"\tGETTING ARTICLE TOPICS")
        topics = []
        if soup:
            for order, link in enumerate(soup, start=1):
                topics.append(
                    ArticleTopic(
                        link['href'],
                        article_url,
                        link.text.strip().upper(),
                        order
                    )
                )
        return topics

    def _get_article_hyperlinks(self, soup, article_url: str):
        Logger.info(f"\tGETTING ARTICLE HYPERLINKS")
        hyperlinks = []
        if soup:
            for order, link in enumerate(soup, start=1):
                hyperlinks.append(
                    ArticleHyperlink(
                        link['href'],
                        article_url,
                        order,
                        link.text.strip().upper(),
                    )
                )
        return hyperlinks

    def _get_article_categories(self, soup, article_url: str):
        Logger.info(f"\tGETTING ARTICLE CATEGORIES")
        categories = []
        if soup:
            for order, link in enumerate(soup, start=1):
                categories.append(
                    ArticleCategory(
                        link['href'],
                        article_url,
                        link.text.strip().upper(),
                    )
                )
        return categories

    def _get_document_medias(self, soup, article_url: str):
        Logger.info(f"\tGETTING ARTICLE MEDIAS")
        medias = []
        for media_tag in ['video', 'audio', 'img']:
            for order, tag in enumerate(soup.findChildren(media_tag, {'src': True}), start=1):
                medias.append(
                    ArticleMedia(
                        tag['src'],
                        article_url,
                        order,
                        media_tag.upper(),
                    )
                )
        for order, video_embed_div in enumerate(soup.findChildren('div', {'class': 'video-embed-wrapper'}), start=1):
            video_iframe = video_embed_div.findChild('iframe', {'src': True})
            medias.append(
                ArticleMedia(
                    video_iframe['src'],
                    article_url,
                    order,
                    'VIDEO'
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

    def _save_to_file(self, file_path: str, file_name: str, content_str: str):
        os.makedirs(file_path, exist_ok=True)
        with open(os.path.join(file_path, file_name), 'w', encoding='utf-8') as arq:
            arq.write(content_str)


class AcriticaScraper(WebScraper):

    DIV_ARTICLE_BLOCK_CLASS = 'eOExTH'
    DIV_ARTICLE_SECTION_CLASS = 'eaVrfa'
    SPAN_HAT_CLASS = 'fCwtAq'
    DIV_META_CLASS = 'Block__Component-sc-1uj1scg-0 fTFJxo article_style acritica'

    def __init__(self, load_wait: int, from_timestamp: float, to_timestamp: float, save_html: bool, save_txt: bool, save_db: bool):
        WebScraper.__init__(self, load_wait, from_timestamp, to_timestamp, save_html, save_txt, save_db)
        self._BASE_URL = r'https://www.acritica.com'
        self._NAME = 'AcriticaScraper'

    def _get_document_links(self, browser, search_term: str):
        Logger.info(f'GETTING ARTICLES FOR SEARCH TERM="{search_term}" ')
        document_links = set()
        page_number = 1
        browser.get(f'{self.get_base_url()}/page/{page_number}/{search_term}')
        sleep(self.get_load_waiting_time())
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        div_article_list = soup.find('div', {'class': AcriticaScraper.DIV_ARTICLE_BLOCK_CLASS})
        links = div_article_list.findChildren('a', {'class': AcriticaScraper.DIV_ARTICLE_SECTION_CLASS, 'href': True})

        while links:
            for link in links:
                article_url = link['href']
                document_links.add(article_url)
                Logger.info(f'\tARTICLE FOUND: {article_url}')
            page_number += 1
            browser.get(f'{self.get_base_url()}/page/{page_number}/{search_term}')
            sleep(self.get_load_waiting_time())
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            div_article_list = soup.find('div', {'class': AcriticaScraper.DIV_ARTICLE_BLOCK_CLASS})
            links = div_article_list.findChildren('a', {'class': AcriticaScraper.DIV_ARTICLE_SECTION_CLASS, 'href': True})

        return document_links

    def _get_article_metadata(self, soup):
        Logger.info(f"\tGETTING ARTICLE METADATA")
        article_metadata = WebScraper._get_article_metadata(self, soup)
        hat_span = soup.find('span', {'class': AcriticaScraper.SPAN_HAT_CLASS})
        article_metadata[ArticleParser.ARTICLE_HAT_PROPERTY] = hat_span.text.upper().strip() if hat_span else None

        div_content = soup.find('div', class_=AcriticaScraper.DIV_META_CLASS)
        article_metadata['content'] = div_content.text.upper()

        return article_metadata

    def _get_document(self, browser, page_url: str):
        document_url = f'{self.get_base_url()}{page_url}'
        Logger.info(f"DOWNLOADING ARTICLE: {document_url}")
        browser.get(document_url)
        sleep(self.get_load_waiting_time())
        soup = BeautifulSoup(browser.page_source, 'html.parser')

        article_metadata = self._get_article_metadata(soup)
        article = ArticleParser.parse_article(article_metadata)

        if not self._FROM_TIMESTAMP < datetime.strptime(article.published, '%Y-%m-%d %H:%M:%S').timestamp() < self._TO_TIMESTAMP:
            Logger.warn(f"\tARTICLE DATETIME IS OUT OF SEARCH INTERVAL")
            return

        article_filename = ''.join([x.upper() for x in article.title if x.isalnum() or x.isspace()])
        article_filename = article_filename.replace(' ', '_')
        if self._SAVE_HTML:
            Logger.info(f"\tSAVING ARTICLE HTML")
            AcriticaScraper._save_to_file(
                self,
                os.path.join(os.getcwd(), 'html'),
                f'{article_filename}.html',
                soup.prettify()
            )

        if self._SAVE_TXT:
            Logger.info(f"\tSAVING ARTICLE CONTENT TO TXT FILE")
            AcriticaScraper._save_to_file(
                self,
                os.path.join(os.getcwd(), 'txt'),
                f'{article_filename}.txt',
                re.sub(r"\s+", " ", ''.join(article_metadata['content']).upper())
            )

        if self._SAVE_DB:
            Logger.info(f"\tSAVING ARTICLE INTO DATABASE")
            ArticleController.insert_one(article)
            article_row = ArticleController.fetch_by_text_field(article.article_url, 'article_url')
            article = Article.from_tuple(article_row[0])

            div_content = soup.find('div', {'class': 'gzQsJ'})
            topics = WebScraper._get_article_topics(
                self,
                div_content.findChildren('a', {'class': 'knlcwJ', 'href': True}),
                article.article_id
            )
            Logger.info(f"\t\ttSAVING ARTICLE TOPICS INTO DATABASE")
            for topic in topics:
                ArticleTopicController.insert_one(topic)

            hyperlinks = WebScraper._get_article_hyperlinks(
                self,
                div_content.findChildren('a', {'href': True}),
                article.article_id
            )
            Logger.info(f"\t\tSAVING ARTICLE HYPERLINKS INTO DATABASE")
            for hyperlink in hyperlinks:
                ArticleHyperlinkController.insert_one(hyperlink)

            categories = self._get_article_categories(soup, article.article_id)
            Logger.info(f"\t\tSAVING ARTICLE CATEGORIES INTO DATABASE")
            for category in categories:
                ArticleCategoryController.insert_one(category)

            medias = WebScraper._get_document_medias(self, div_content, article.article_id)
            Logger.info(f"\t\tSAVING ARTICLE MEDIAS INTO DATABASE")
            for media in medias:
                ArticleMediaController.insert_one(media)

    def _get_article_categories(self, soup, article_url: str):
        Logger.info(f"\tGETTING ARTICLE CATEGORIES")
        meta_url = soup.find('meta', {'property': 'og:url', 'content': True})
        document_url = meta_url['content']
        document_url = document_url.replace(self.get_base_url(), '')
        categories = []
        cat_paths = document_url.split('/')
        if cat_paths and len(cat_paths) > 2:
            for order, path in enumerate(cat_paths[1:-1], start=1):
                categories.append(
                    ArticleCategory(
                        f'/{path}',
                        article_url,
                        path.strip().upper(),
                    )
                )
        return categories


class PortalAmazoniaScraper(WebScraper):

    def __init__(self, load_wait: int, from_timestamp: float, to_timestamp: float, save_html: bool, save_txt: bool, save_db: bool):
        WebScraper.__init__(self, load_wait, from_timestamp, to_timestamp, save_html, save_txt, save_db)
        self._BASE_URL = r'https://portalamazonia.com'
        self._NAME = 'PortalAmazoniaScraper'

    def _get_article_metadata(self, soup):
        article_metadata = WebScraper._get_article_metadata(self, soup)

        div_id = soup.find('div', {'data-id': True})

        span_author = div_id.findChild('span', {'class': 'eb-meta-author', 'itemprop': 'author'})
        article_metadata[
            ArticleParser.ARTICLE_AUTHOR_PROPERTY] = span_author.text.upper().strip() if span_author else None

        article_metadata[ArticleParser.ARTICLE_PUBLISHED_PROPERTY] = soup.find('time', {'itemprop': 'datePublished'}).text.strip()
        article_metadata[ArticleParser.ARTICLE_MODIFIED_PROPERTY] = soup.find('time', {'itemprop': 'dateModified'}).text.strip()

        article_metadata['content'] = div_id.text.upper()
        return article_metadata

    def _get_document_links(self, search_term: str, browser):
        article_links = set()
        browser.get(f'{self.get_base_url()}/busca?q={search_term}')
        sleep(self.get_load_waiting_time())
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        for div_item in soup.find_all('div', {'class': 'result-item'}):
            article_links.add(div_item.findChild('a', {'href': True})['href'])

        if soup.find('ul', {'class': 'pagination'}):
            page = 1
            while True:
                browser.get(f'{self.get_base_url()}/busca?q={search_term}&start={page * 20}')
                sleep(self.get_load_waiting_time())
                soup = BeautifulSoup(browser.page_source, 'html.parser')
                items = soup.find_all('div', {'class': 'result-item'})
                if not items:
                    break
                for item in items:
                    article_links.add(item.findChild('a', {'href': True})['href'])
                page += 1
        return article_links

    def _get_document(self, browser, page_url: str):
        document_url = f'{self.get_base_url()}{page_url}'
        browser.get(page_url)
        sleep(self.get_load_waiting_time())
        soup = BeautifulSoup(browser.page_source, 'html.parser')

        article_metadata = self._get_article_metadata(soup)
        article = ArticleParser.parse_article(article_metadata)

        if not self._FROM_TIMESTAMP < datetime.strptime(article.published, '%Y-%m-%d %H:%M').timestamp() < self._TO_TIMESTAMP:
            return

        if self._SAVE_HTML:
            PortalAmazoniaScraper._save_html(
                self,
                page_url,
                soup.prettify()
            )

        if self._SAVE_TXT:
            PortalAmazoniaScraper._save_txt(
                self,
                document_url,
                re.sub(r"\s+", " ", ''.join(article_metadata['content']).upper())
            )

        if self._SAVE_DB:
            ArticleController.insert_one(article)
            article_row = ArticleController.fetch_by_text_field(article.article_url, 'article_url')
            article = Article.from_tuple(article_row[0])

            div_content = soup.find('div', {'id': True, 'class': 'eb-entry', 'data-id': True, 'data-uid': True})

            cell_tags = div_content.find('div', {'class': 'cell-tags'})
            topics = WebScraper._get_article_topics(
                self,
                cell_tags.findChildren('a', {'href': True}) if cell_tags else None,
                article.article_id
            )
            for topic in topics:
                ArticleTopicController.insert_one(topic)

            hyperlinks = WebScraper._get_article_hyperlinks(
                self,
                div_content.findChildren('a', {'href': True}),
                article.article_id
            )
            for hyperlink in hyperlinks:
                ArticleHyperlinkController.insert_one(hyperlink)

            div_categories = soup.findChild('div', {'class': 'eb-meta-category'})
            categories = WebScraper._get_article_categories(
                self,
                div_categories.findChildren('a', {'href': True}),
                article.article_id
            )
            for category in categories:
                ArticleCategoryController.insert_one(category)

            medias = WebScraper._get_document_medias(self, div_content, article.article_id)
            for media in medias:
                ArticleMediaController.insert_one(media)


class G1Scraper(WebScraper):

    def __init__(self, load_wait: int, from_timestamp: float, to_timestamp: float, save_html: bool, save_txt: bool, save_db: bool):
        WebScraper.__init__(self, load_wait, from_timestamp, to_timestamp, save_html, save_txt, save_db)
        self._BASE_URL = r'https://g1.globo.com'
        self._NAME = 'G1Scraper'

    def _get_article_metadata(self, soup):
        article_metadata = WebScraper._get_article_metadata(self, soup)
        article_metadata['og:url'] = article_metadata['og:url'].lower()

        body = soup.find('body', {'data-content-id': True})
        if not body:
            body = soup.find('div', {'id': 'glb-materia'})
        elif not body:
            print('')

        span_author = body.find('p', {'class': 'content-publication-data__from', 'title': True})
        if not span_author:
            span_author = body.find('p', class_='vcard author')
        elif not span_author:
            print('')
        article_metadata[ArticleParser.ARTICLE_AUTHOR_PROPERTY] = span_author.text.upper().strip()[4:] if span_author else None

        published_str = body.find('time', {'itemprop': 'datePublished'})
        modified_str = body.find('time', {'itemprop': 'dateModified'})
        dt_fmt = '%Y-%m-%dT%H:%M:%S.%fZ'
        if not published_str:
            published_str = {'datetime': body.find('abbr', class_='published').text}
            modified_str = {'datetime': body.find('abbr', class_='updated').text}
            dt_fmt = '%d/%m/%Y %Hh%M'
        elif not published_str:
            print('')

        article_metadata[ArticleParser.ARTICLE_PUBLISHED_PROPERTY] = datetime.strptime(published_str['datetime'], dt_fmt)
        article_metadata[ArticleParser.ARTICLE_MODIFIED_PROPERTY] = datetime.strptime(modified_str['datetime'], dt_fmt)

        div_content = body.find('article', {'itemprop': 'articleBody'})
        if not div_content:
            div_content = soup.find('div', {'id': 'glb-materia'})

        article_metadata['content'] = div_content.text.upper()
        return article_metadata

    def _get_document_links(self, browser, search_term: str):
        article_links = set()
        from_str = datetime.fromtimestamp(self._FROM_TIMESTAMP).strftime('%Y-%m-%dT00:00:00-0400').replace(':', '%3A')
        to_str = datetime.fromtimestamp(self._TO_TIMESTAMP).strftime('%Y-%m-%dT23:59:59-0400').replace(':', '%3A')

        page = 1
        browser.get(f'{self.get_base_url()}/busca/?q={search_term}&page={page}&order=recent&from={from_str}&to={to_str}&species=notícias')
        sleep(self.get_load_waiting_time())
        soup = BeautifulSoup(browser.page_source, 'html.parser')

        div_pagination = True
        while div_pagination:
            for div_item in soup.find_all('li', {'data-position': True}, class_='widget widget--card widget--info'):
                a_link = div_item.findChild('div', class_='widget--info__text-container').findChild('a', {'href': True})
                link = a_link['href']
                start_index = link.index('&u=https') + 3
                end_index = link.index('&syn')
                article_links.add(urllib.parse.unquote(link[start_index: end_index]))
            page += 1
            browser.get(f'{self.get_base_url()}/busca/?q={search_term}&page={page}&order=recent&from={from_str}&to={to_str}&species=notícias')
            sleep(self.get_load_waiting_time())
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            div_pagination = soup.find('div', class_='pagination widget')

        return article_links

    def _get_document(self, browser, page_url: str):
        browser.get(page_url)
        sleep(self.get_load_waiting_time())
        soup = BeautifulSoup(browser.page_source, 'html.parser')

        article_metadata = self._get_article_metadata(soup)
        article = ArticleParser.parse_article(article_metadata)

        if self._SAVE_HTML:
            G1Scraper._save_html(
                self,
                page_url,
                soup.prettify()
            )
        if self._SAVE_TXT:
            G1Scraper._save_txt(
                self,
                page_url,
                article_metadata['content'].upper()
            )
        if self._SAVE_DB:
            ArticleController.insert_one(article)
            article_row = ArticleController.fetch_by_text_field(article.article_url, 'article_url')
            article = Article.from_tuple(article_row[0])

            div_content = soup.find('article', {'itemprop': 'articleBody'})
            if not div_content:
                div_content = soup.find('div', {'id': 'glb-materia'})

            cell_tags = div_content.find('ul', {'class': 'entities__list-item'})
            if not cell_tags:
                cell_tags = div_content.findChild('div', {'class': 'lista-de-entidades'})
            topics = WebScraper._get_article_topics(
                self,
                cell_tags.findChildren('a', {'href': True}) if cell_tags else None,
                article.article_id
            )
            for topic in topics:
                ArticleTopicController.insert_one(topic)

            hyperlinks = WebScraper._get_article_hyperlinks(self, div_content.findChildren('a', {'href': True}), article.article_id)
            for hyperlink in hyperlinks:
                ArticleHyperlinkController.insert_one(hyperlink)

            div_categories = soup.findAll('a', {'href': True}, class_='header-editoria--link ellip-line')
            categories = WebScraper._get_article_categories(self, div_categories, article.article_id)
            for category in categories:
                ArticleCategoryController.insert_one(category)

            medias = G1Scraper._get_document_medias(self, div_content, article.article_id)
            for media in medias:
                ArticleMediaController.insert_one(media)

    def _get_document_medias(self, soup, article_url: str):
        medias = []
        for media_tag in ['video', 'audio', 'img']:
            for order, tag in enumerate(soup.findChildren(media_tag, {'src': True}), start=1):
                medias.append(
                    ArticleMedia(
                        tag['src'],
                        article_url,
                        order,
                        media_tag.upper()
                    )
                )
        for order, video_embed_div in enumerate(soup.findChildren('div', {'itemtype': 'http://schema.org/VideoObject', 'itemprop':'video'}), start=1):
            metas = video_embed_div.findChildren('meta', {'itemprop': True})
            for meta in metas:
                if str(meta['itemprop']).lower() == 'contenturl':
                    medias.append(
                        ArticleMedia(
                            meta['content'],
                            article_url,
                            order,
                            'VIDEO',
                        )
                    )
        return medias
