# -*- coding: utf-8 -*-
import re
from time import sleep
from typing import List
from bs4 import BeautifulSoup
from bs4.element import Comment
from selenium import webdriver

from model import AcriticaParser


class AcriticaCrawler:

    PORTAL_BASE_URL = r'https://www.acritica.com'
    DEFAULT_LOAD_WAIT_TIME = 5

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
    def find_news(terms: List[str]):
        news_links = []
        browser = webdriver.Chrome()
        browser.maximize_window()
        for term in terms:
            browser.get(f'{AcriticaCrawler.PORTAL_BASE_URL}/?term={term}')
            sleep(AcriticaCrawler.DEFAULT_LOAD_WAIT_TIME)
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            div = soup.find('div', {'class': 'ecqOwd'})  # Block__Component-sc-1uj1scg-0 ekRQuY
            search_data = re.search(f'RESULTADO DA PESQUISAVocê pesquisou por {term}Foram encontrados (\d+) resultadosEsta é a página (\d+) de (\d+)', div.text).groups()
            # search_results = int(search_data[0])
            search_pages = int(search_data[2])

            for i in range(1, search_pages+1):
                browser.get(f'{AcriticaCrawler.PORTAL_BASE_URL}/page/{i}/{term}')
                sleep(AcriticaCrawler.DEFAULT_LOAD_WAIT_TIME)
                soup = BeautifulSoup(browser.page_source, 'html.parser')
                links = soup.findAll('a', {'class': 'dDfqGJ', 'href': True})
                news_links.extend([str(link['href']) for link in links])
                break
        browser.close()
        return news_links

    @staticmethod
    def get_articles(articles_urls: List[str]):
        articles = []
        browser = webdriver.Chrome()
        browser.maximize_window()
        for articles_url in articles_urls:
            browser.get(f'{AcriticaCrawler.PORTAL_BASE_URL}{articles_url}')
            sleep(AcriticaCrawler.DEFAULT_LOAD_WAIT_TIME)
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            article_data = {meta['property']: str(meta['content']).upper().strip() for meta in soup.findAll('meta', {'property': True})}
            cat_span = soup.find('span', {'class': 'ceiOww'})
            article_data['article_id'] = 'AC' + article_data['og:url'][article_data['og:url'].rindex('.')+1:]
            article_data['header'] = cat_span.text.upper().strip() if cat_span else None
            url_parts = article_data['og:url'].split('/')
            article_data['editorial'] = str(url_parts[1]).strip().upper() if len(url_parts) > 2 else None
            tags = soup.findAll('span', {'class': 'gCiqnR'})

            if tags:
                article_data['tags'] = '#'.join([tag.text.strip().upper() for tag in tags])
            else:
                article_data['tags'] = None

            article_content = []
            for div in soup.findAll('div', {'class': 'bVxWXz'}):
                for element in div.findChildren():
                    if AcriticaCrawler.tag_visible(element) and not element.findChild() and element.text:
                        print(element.text)
                        article_content.append(element.text)

            article_data['content'] = '\n'.join(article_content).upper()
            AcriticaCrawler.save_article_html(f"html/{article_data['article_id']}.html", soup.prettify())
            articles.append(AcriticaParser.parse_article(article_data))
        browser.close()
        return articles

    @staticmethod
    def save_article_html(file_name: str, html: str):
        with open(file_name, 'w', encoding='utf-8') as arq:
            arq.write(html)

