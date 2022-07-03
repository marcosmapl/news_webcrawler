# -*- coding: utf-8 -*-
import re
from time import sleep
from typing import List
from bs4 import BeautifulSoup
from selenium import webdriver


class AcriticaCrawler:

    __PORTAL_BASE_URL = r'https://www.acritica.com/'
    __DEFAULT_LOAD_WAIT_TIME = 3

    @classmethod
    def find_news(cls, terms: List[str]):
        news_links = []
        browser = webdriver.Chrome()
        browser.maximize_window()
        for term in terms:
            browser.get(f'{cls.__PORTAL_BASE_URL}/?term={term}')
            sleep(AcriticaCrawler.__DEFAULT_LOAD_WAIT_TIME)
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            div = soup.find('div', {'class': 'ecqOwd'})  # Block__Component-sc-1uj1scg-0 ekRQuY
            search_data = re.search(f'RESULTADO DA PESQUISAVocê pesquisou por {term}Foram encontrados (\d+) resultadosEsta é a página (\d+) de (\d+)', div.text).groups()
            # search_results = int(search_data[0])
            search_pages = int(search_data[2])

            for i in range(1, search_pages+1):
                browser.get(f'{cls.__PORTAL_BASE_URL}/page/{i}/{term}')
                sleep(AcriticaCrawler.__DEFAULT_LOAD_WAIT_TIME)
                soup = BeautifulSoup(browser.page_source, 'html.parser')
                links = soup.findAll('a', {'class': 'dDfqGJ', 'href': True})
                news_links.extend([link['href'] for link in links])
                break
        browser.close()
        return news_links

    @classmethod
    def get_articles(cls, articles_urls: str):
        articles = []
        browser = webdriver.Chrome()
        browser.maximize_window()
        for article_link in articles_urls:
            browser.get(f'{cls.__PORTAL_BASE_URL}{article_link}')
            sleep(AcriticaCrawler.__DEFAULT_LOAD_WAIT_TIME)
            soup = BeautifulSoup(browser.page_source, 'html.parser')
            article_data = {meta['property']: str(meta['content']).upper() for meta in soup.findAll('meta', {'property': True})}
            cat_span = soup.find('span', {'class': 'ceiOww'})
            article_data['og:category'] = cat_span.text if cat_span else None
            articles.append(article_data)
        browser.close()
        return articles

