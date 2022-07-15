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
    def get_document_medias(soup, article_id: str):
        medias = []
        for media_tag in ['video', 'audio']:
            for order, tag in enumerate(soup.find_all(media_tag, {'src': True}), start=1):
                medias.append(ArticleMedia(
                    article_id,
                    order,
                    tag['type'],
                    tag['src']
                ))

        for order, video_embed_div in enumerate(soup.find_all('div', {'class': 'video-embed-wrapper'}), start=1):
            video_iframe = video_embed_div.findChild('iframe', {'src': True})
            medias.append(ArticleMedia(
                article_id,
                order,
                'YOUTUBE/VIDEO',
                video_iframe['src']
            ))

        return medias

    @staticmethod
    def get_base_url():
        pass

    @staticmethod
    def tag_visible(element):
        if element.parent.name in [
            'style', 'script', 'head', 'title', 'meta', '[document]'
        ]:
            return False
        if isinstance(element, Comment):
            return False
        return True

    @staticmethod
    def create_output_dirs():
        pass

    @staticmethod
    def save_document_to_file(file_path: str, text: str):
        with open(file_path, 'w', encoding='utf-8') as arq:
            arq.write(text)


class AcriticaScraper(WebScraper):

    DEFAULT_LOAD_WAIT_TIME = 3
    __SCRAPER_HTML_FOLDER = 'acritica/html'
    __SCRAPER_TXT_FOLDER = 'acritica/txt'

    @staticmethod
    def get_base_url():
        return r'https://www.acritica.com'

    @staticmethod
    def create_output_dirs():
        if not os.path.isdir(os.path.join(os.getcwd(), 'acritica', 'html')):
            os.mkdir(os.path.join(os.getcwd(), 'acritica', 'html'))
        if not os.path.isdir(os.path.join(os.getcwd(), 'acritica', 'txt')):
            os.mkdir(os.path.join(os.getcwd(), 'acritica', 'txt'))

    @staticmethod
    def get_document_links(search_term: List[str], browser):
        article_links = set()
        for term in search_term:
            browser.get(f'{AcriticaScraper.get_base_url()}/?term={term}')
            sleep(AcriticaScraper.DEFAULT_LOAD_WAIT_TIME)
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            div = soup.find('div', {'class': 'ecqOwd'})  # Block__Component-sc-1uj1scg-0 ekRQuY
            search_data = re.search(f'RESULTADO DA PESQUISAVocê pesquisou por {term}Foram encontrados (\d+) resultadosEsta é a página (\d+) de (\d+)', div.text).groups()
            # search_results = int(search_data[0])
            search_pages = int(search_data[2])

            for i in range(1, search_pages+1):
                browser.get(f'{AcriticaScraper.get_base_url()}/page/{i}/{term}')
                sleep(AcriticaScraper.DEFAULT_LOAD_WAIT_TIME)
                soup = BeautifulSoup(browser.page_source, 'html.parser')
                links = soup.findAll('a', {'class': 'dDfqGJ', 'href': True})
                for link in links:
                    article_url = str(link['href'])
                    article_links.add(article_url)
                    print(f"MATERIA ADICIONADA A LISTA DE DOWNLOAD: {article_url}\nTOTAL {len(article_links)}")
        return article_links

    @staticmethod
    def get_document(document_url: str, browser):
        document_url = f'{AcriticaScraper.get_base_url()}{document_url}'
        print(f"BAIXANDO MATERIA: {document_url}")
        browser.get(document_url)
        sleep(AcriticaScraper.DEFAULT_LOAD_WAIT_TIME)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        try:
            article_data = {meta['property']: str(meta['content']).upper().strip() for meta in soup.findAll('meta', {'property': True})}
            article_data[ArticleParser.ARTICLE_ID_PROPERTY] = 'AC' + article_data['og:url'][article_data['og:url'].rindex('.')+1:]
            hat_span = soup.find('span', {'class': 'ceiOww'})
            article_data[ArticleParser.ARTICLE_HAT_PROPERTY] = hat_span.text.upper().strip() if hat_span else None
            url_parts = document_url.split('/')
            article_data[ArticleParser.ARTICLE_EDITORIAL_PROPERTY] = str(url_parts[1]).strip().upper() if len(url_parts) > 2 else None
            tags = soup.findAll('span', {'class': 'gCiqnR'})

            if tags:
                article_data['tags'] = '#'.join([tag.text.strip().upper() for tag in tags])
            else:
                article_data['tags'] = None

            article_content = []
            for div in soup.findAll('div', {'class': 'bVxWXz'}):
                for element in div.findChildren():
                    if AcriticaScraper.tag_visible(element) and not element.findChild() and element.text:
                        article_content.append(element.text)

            AcriticaScraper.save_document_to_file(
                os.path.join(
                    os.getcwd(),
                    'acritica',
                    'html',
                    f"{article_data['article_id']}.html"
                ),
                soup.prettify()
            )

            AcriticaScraper.save_document_to_file(
                os.path.join(
                    os.getcwd(),
                    'acritica',
                    'txt',
                    f"{article_data['article_id']}.txt"
                ),
                ''.join(article_content).upper()
            )

            return ArticleParser.parse_article(article_data)
        except Exception as err:
            print(str(err))


class PortalAmazoniaScraper(WebScraper):

    DEFAULT_LOAD_WAIT_TIME = 3

    @staticmethod
    def _get_article_metadata(soup):
        article_metadata = {meta['property']: str(meta['content']).strip().upper() for meta in soup.findAll('meta', {'property': True})}

        div_id = soup.find('div', {'data-id': True})
        article_metadata[ArticleParser.ARTICLE_ID_PROPERTY] = 'PAM' + div_id['data-id']

        span_author = div_id.findChild('span', {'class': 'eb-meta-author', 'itemprop': 'author'})
        article_metadata[ArticleParser.ARTICLE_AUTHOR_PROPERTY] = span_author.text.upper().strip() if span_author else None

        article_metadata[ArticleParser.ARTICLE_PUBLISHED_PROPERTY] = soup.find('time', {'itemprop': 'datePublished'}).text.strip()
        article_metadata[ArticleParser.ARTICLE_MODIFIED_PROPERTY] = soup.find('time', {'itemprop': 'dateModified'}).text.strip()

        article_metadata['content'] = div_id.text.upper()
        return article_metadata

    @staticmethod
    def _get_article_topics(soup, article_id):
        topics = []
        div_topics = soup.find('div', {'class': 'cell-tags'})
        if div_topics:
            for order, topic in enumerate(div_topics.findChildren('a', {'href': True}), start=1):
                topics.append(
                    ArticleTopic(
                        article_id,
                        topic.text.strip().upper(),
                        topic['href'],
                        order
                    )
                )
        return topics

    @staticmethod
    def _get_article_images(soup, article_id: str):
        images = []
        imgs = soup.findChildren('img', {'src': True})
        if imgs:
            for order, img in enumerate(imgs, start=1):
                images.append(
                    ArticleImage(
                        article_id,
                        img['src'],
                        order,
                        int(img['height']) if img.has_attr('height') else None,
                        int(img['width']) if img.has_attr('width') else None,
                        os.path.splitext(img['src'])[-1].strip().upper())
                )
        return images

    @staticmethod
    def _get_article_hyperlinks(soup, article_id: str):
        hyperlinks = []
        a_links = soup.findChildren('a', {'href': True})
        if a_links:
            for order, link in enumerate(a_links, start=1):
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
    def _get_article_categories(soup, article_id: str):
        categories = []
        div_categories = soup.findChild('div', {'class': 'eb-meta-category'})
        a_categories = div_categories.findChildren('a', {'href': True})
        if a_categories:
            for order, link in enumerate(a_categories, start=1):
                categories.append(
                    ArticleCategory(
                        article_id,
                        link.text.strip().upper(),
                        link['href']
                    )
                )
        return categories

    @staticmethod
    def get_base_url():
        return r'https://portalamazonia.com'

    @staticmethod
    def create_output_dirs():
        if not os.path.isdir(os.path.join(os.getcwd(), 'portal_amazonia', 'html')):
            os.makedirs(os.path.join(os.getcwd(), 'portal_amazonia', 'html'))
        if not os.path.isdir(os.path.join(os.getcwd(), 'portal_amazonia', 'txt')):
            os.makedirs(os.path.join(os.getcwd(), 'portal_amazonia', 'txt'))

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
        try:
            article_metadata = PortalAmazoniaScraper._get_article_metadata(soup)
            article = ArticleParser.parse_article(article_metadata)

            div_content = soup.find('div', {'id': True, 'class': 'eb-entry', 'data-id': True, 'data-uid': True})

            topics = PortalAmazoniaScraper._get_article_topics(div_content, article.article_id)
            images = PortalAmazoniaScraper._get_article_images(div_content, article.article_id)
            medias = PortalAmazoniaScraper.get_document_medias(div_content, article.article_id)
            hyperlinks = PortalAmazoniaScraper._get_article_hyperlinks(div_content, article.article_id)
            categories = PortalAmazoniaScraper._get_article_categories(div_content, article.article_id)

            AcriticaScraper.save_document_to_file(
                os.path.join(
                    os.getcwd(),
                    'portal_amazonia',
                    'html',
                    f"{article.article_id}.html"
                ),
                soup.prettify()
            )

            AcriticaScraper.save_document_to_file(
                os.path.join(
                    os.getcwd(),
                    'portal_amazonia',
                    'txt',
                    f"{article.article_id}.txt"
                ),
                re.sub(r"\s+", " ", ''.join(article_metadata['content']).upper())
            )

            return article, topics, images, medias, hyperlinks, categories
        except Exception as err:
            print(str(err))
