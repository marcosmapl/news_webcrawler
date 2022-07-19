# -*- coding: utf-8 -*-
import os
import re
from time import sleep
from typing import List

from bs4 import BeautifulSoup
from bs4.element import Comment

from model import ArticleParser, ArticleImage, ArticleTopic, ArticleMedia, ArticleHyperlink, ArticleCategory


class WebScraper:

    @staticmethod
    def get_document_links(search_term: List[str], browser):
        pass

    @staticmethod
    def get_document(document_url: str, browser):
        pass

    @staticmethod
    def get_article_metadata(soup):
        return {meta['property']: str(meta['content']).upper().strip() for meta in soup.findAll('meta', {'property': True})}

    @staticmethod
    def get_article_topics(soup, article_id):
        topics = []
        if soup:
            for order, link in enumerate(soup, start=1):
                topics.append(
                    ArticleTopic(
                        article_id,
                        link.text.strip().upper(),
                        link['href'],
                        order
                    )
                )
        return topics

    @staticmethod
    def get_article_images(soup, article_id):
        images = []
        if soup:
            for order, img in enumerate(soup, start=1):
                img_src = img['src']
                img_ext = re.search("\.JPG|\.JPEG|\.GIF|\.PNG|\.EPS|.GIF|.TIFF|.RAW", img_src.upper())
                images.append(
                    ArticleImage(
                        article_id,
                        img['src'],
                        order,
                        int(img['height']) if img.has_attr('height') else None,
                        int(img['width']) if img.has_attr('width') else None,
                        str(img_ext.group())
                    )
                )
        return images

    @staticmethod
    def get_article_hyperlinks(soup, article_id: str):
        hyperlinks = []
        if soup:
            for order, link in enumerate(soup, start=1):
                hyperlinks.append(
                    ArticleHyperlink(
                        article_id,
                        order,
                        link.text.strip().upper(),
                        link['href']
                    )
                )
        return hyperlinks

    @staticmethod
    def get_article_categories(soup, article_id: str):
        categories = []
        if soup:
            for order, link in enumerate(soup, start=1):
                categories.append(
                    ArticleCategory(
                        article_id,
                        link.text.strip().upper(),
                        link['href']
                    )
                )
        return categories

    @staticmethod
    def get_document_medias(soup, article_id: str):
        medias = []
        for media_tag in ['video', 'audio']:
            for order, tag in enumerate(soup.findChildren(media_tag, {'src': True}), start=1):
                medias.append(ArticleMedia(
                    article_id,
                    order,
                    tag['type'],
                    tag['src']
                ))
        for order, video_embed_div in enumerate(soup.findChildren('div', {'class': 'video-embed-wrapper'}), start=1):
            video_iframe = video_embed_div.findChild('iframe', {'src': True})
            medias.append(ArticleMedia(
                article_id,
                order,
                'YOUTUBE/VIDEO',
                video_iframe['src']
            ))

        return medias

    @staticmethod
    def tag_visible(element):
        if element.parent.name in [
            'style', 'script', 'head', 'title', 'meta', '[document]'
        ]:
            return False
        if isinstance(element, Comment):
            return False
        return True

    @classmethod
    def save_html(cls, article_id: str, html: str):
        WebScraper.__save_document_to_file(
            os.path.join(
                os.getcwd(),
                cls.get_scrapper_name(),
                'html',
                f"{article_id}.html"
            ),
            html
        )

    @classmethod
    def save_txt(cls, article_id: str, txt: str):
        WebScraper.__save_document_to_file(
            os.path.join(
                os.getcwd(),
                cls.get_scrapper_name(),
                'txt',
                f"{article_id}.txt"
            ),
            txt
        )

    @staticmethod
    def __save_document_to_file(file_path: str, text: str):
        with open(file_path, 'w', encoding='utf-8') as arq:
            arq.write(text)

    @classmethod
    def create_output_dirs(cls):
        if not os.path.isdir(os.path.join(os.getcwd(), cls.get_scrapper_name(), 'html')):
            os.makedirs(os.path.join(os.getcwd(), cls.get_scrapper_name(), 'html'))
        if not os.path.isdir(os.path.join(os.getcwd(), cls.get_scrapper_name(), 'txt')):
            os.makedirs(os.path.join(os.getcwd(), cls.get_scrapper_name(), 'txt'))

    @staticmethod
    def get_scrapper_name():
        return 'scraper'

    @staticmethod
    def get_base_url():
        pass


class AcriticaScraper(WebScraper):

    DEFAULT_LOAD_WAIT_TIME = 3

    @staticmethod
    def get_base_url():
        return r'https://www.acritica.com'

    @staticmethod
    def get_scrapper_name():
        return 'acritica'

    @staticmethod
    def get_article_metadata(soup):
        article_metadata = WebScraper.get_article_metadata(soup)
        article_metadata[ArticleParser.ARTICLE_ID_PROPERTY] = 'AC' + article_metadata['og:url'][article_metadata['og:url'].rindex('.') + 1:]
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

    @staticmethod
    def get_document_links(search_term: List[str], browser):
        article_links = set()
        for term in search_term:
            i = 1
            while True:
                browser.get(f'{AcriticaScraper.get_base_url()}/page/{i}/{term}')
                sleep(AcriticaScraper.DEFAULT_LOAD_WAIT_TIME)
                soup = BeautifulSoup(browser.page_source, 'html.parser')
                div_article_list = soup.find('div', {'class': 'bwIhbp'})
                links = div_article_list.findChildren('a', {'class': 'dDfqGJ', 'href': True})
                if links:
                    i += 1
                    for link in links:
                        article_links.add(link['href'])
                        print(f"MATERIA ADICIONADA A LISTA DE DOWNLOAD: {link['href']}\nTOTAL {len(article_links)}")
                else:
                    break
        return article_links

    @staticmethod
    def get_document(document_url: str, browser):
        document_url = f'{AcriticaScraper.get_base_url()}{document_url}'
        print(f"BAIXANDO MATERIA: {document_url}")
        browser.get(document_url)
        sleep(AcriticaScraper.DEFAULT_LOAD_WAIT_TIME)
        soup = BeautifulSoup(browser.page_source, 'html.parser')

        article_metadata = AcriticaScraper.get_article_metadata(soup)
        article = ArticleParser.parse_article(article_metadata)

        div_content = soup.find('div', {'class': 'gzQsJ'})

        topics = AcriticaScraper.get_article_topics(div_content.find('a', {'class': 'knlcwJ', 'href': True}), article.article_id)
        images = AcriticaScraper.get_article_images(div_content.findChildren('img', {'src': True}), article.article_id)
        hyperlinks = AcriticaScraper.get_article_hyperlinks(div_content.findChildren('a', {'href': True}), article.article_id)
        categories = AcriticaScraper.get_article_categories(soup, article.article_id)
        medias = AcriticaScraper.get_document_medias(div_content, article.article_id)

        AcriticaScraper.save_html(article.article_id, soup.prettify())
        AcriticaScraper.save_txt(article.article_id, re.sub(r"\s+", " ", ''.join(article_metadata['content']).upper()))

        return article, topics, images, medias, hyperlinks, categories

    @staticmethod
    def get_article_categories(soup, article_id):
        meta_url = soup.find('meta', {'property': 'og:url', 'content': True})
        document_url = meta_url['content']
        document_url = document_url.replace(AcriticaScraper.get_base_url(), '')
        categories = []
        cat_paths = document_url.split('/')
        if cat_paths and len(cat_paths) > 2:
            for order, path in enumerate(cat_paths[1:-1], start=1):
                categories.append(
                    ArticleCategory(
                        article_id,
                        path.strip().upper(),
                        f'/{path}'
                    )
                )
        return categories


class PortalAmazoniaScraper(WebScraper):

    DEFAULT_LOAD_WAIT_TIME = 3

    @staticmethod
    def get_article_metadata(soup):
        article_metadata = WebScraper.get_article_metadata(soup)

        div_id = soup.find('div', {'data-id': True})
        article_metadata[ArticleParser.ARTICLE_ID_PROPERTY] = 'PAM' + div_id['data-id']

        span_author = div_id.findChild('span', {'class': 'eb-meta-author', 'itemprop': 'author'})
        article_metadata[ArticleParser.ARTICLE_AUTHOR_PROPERTY] = span_author.text.upper().strip() if span_author else None

        article_metadata[ArticleParser.ARTICLE_PUBLISHED_PROPERTY] = soup.find('time', {'itemprop': 'datePublished'}).text.strip()
        article_metadata[ArticleParser.ARTICLE_MODIFIED_PROPERTY] = soup.find('time', {'itemprop': 'dateModified'}).text.strip()

        article_metadata['content'] = div_id.text.upper()
        return article_metadata

    @staticmethod
    def get_base_url():
        return r'https://portalamazonia.com'

    @staticmethod
    def get_scrapper_name():
        return 'portal_amazonia'

    @staticmethod
    def get_document_links(search_term: List[str], browser):
        article_links = set()
        for term in search_term:
            browser.get(f'{PortalAmazoniaScraper.get_base_url()}/busca?q={term}')
            sleep(PortalAmazoniaScraper.DEFAULT_LOAD_WAIT_TIME)
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            for div_item in soup.find_all('div', {'class': 'result-item'}):
                article_links.add(div_item.findChild('a', {'href': True})['href'])

            if soup.find('ul', {'class': 'pagination'}):
                page = 1
                while True:
                    browser.get(f'{PortalAmazoniaScraper.get_base_url()}/busca?q={term}&start={page*20}')
                    sleep(PortalAmazoniaScraper.DEFAULT_LOAD_WAIT_TIME)
                    soup = BeautifulSoup(browser.page_source, 'html.parser')
                    items = soup.find_all('div', {'class': 'result-item'})
                    if not items:
                        break
                    for item in items:
                        article_links.add(item.findChild('a', {'href': True})['href'])
                    page += 1
        return article_links

    @staticmethod
    def get_document(document_url: str, browser):
        document_url = f'{PortalAmazoniaScraper.get_base_url()}{document_url}'
        print(f"BAIXANDO MATERIA: {document_url}")
        browser.get(document_url)
        sleep(AcriticaScraper.DEFAULT_LOAD_WAIT_TIME)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        article_metadata = PortalAmazoniaScraper.get_article_metadata(soup)
        article = ArticleParser.parse_article(article_metadata)

        div_content = soup.find('div', {'id': True, 'class': 'eb-entry', 'data-id': True, 'data-uid': True})

        cell_tags = div_content.find('div', {'class': 'cell-tags'})
        topics = PortalAmazoniaScraper.get_article_topics(cell_tags.findChildren('a', {'href': True}) if cell_tags else None, article.article_id)
        images = PortalAmazoniaScraper.get_article_images(div_content.findChildren('img', {'src': True}), article.article_id)
        hyperlinks = PortalAmazoniaScraper.get_article_hyperlinks(div_content.findChildren('a', {'href': True}), article.article_id)
        div_categories = soup.findChild('div', {'class': 'eb-meta-category'})
        categories = PortalAmazoniaScraper.get_article_categories(div_categories.findChildren('a', {'href': True}), article.article_id)
        medias = PortalAmazoniaScraper.get_document_medias(div_content, article.article_id)

        PortalAmazoniaScraper.save_html(article.article_id, soup.prettify())
        PortalAmazoniaScraper.save_txt(article.article_id, re.sub(r"\s+", " ", ''.join(article_metadata['content']).upper()))

        return article, topics, images, medias, hyperlinks, categories

