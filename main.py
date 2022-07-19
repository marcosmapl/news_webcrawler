# -*- coding: utf-8 -*-
from typing import List

from selenium import webdriver

from scraper import PortalAmazoniaScraper, AcriticaScraper
from database import DatabaseManager, ArticleController, ArticleImageController, ArticleTopicController, ArticleMediaController, ArticleHyperlinkController, \
    ArticleCategoryController
from model import ModelEntity

scrapers = [
    AcriticaScraper,
    PortalAmazoniaScraper
]


def save_elements(controller, elements: List[ModelEntity]):
    for element in elements:
        try:
            controller.insert_one(element)
        except Exception as erro:
            DatabaseManager.close_connection()
            print(erro)


if __name__ == '__main__':
    DatabaseManager.create_database(DatabaseManager.POSTGRESQL_DB)
    for scraper in scrapers:
        scraper.create_output_dirs()

    search_terms = input('DIGITE UM OU MAIS TERMOS DE BUSCA SEPARADOS POR VÍRGULA: ').split(',')
    browser = webdriver.Chrome()
    browser.maximize_window()

    for scraper in scrapers:
        article_links = scraper.get_document_links(search_terms, browser)
        for link in article_links:
            article, topics, images, medias, hyperlinks, categories = scraper.get_document(link, browser)

            save_elements(ArticleController, [article])
            save_elements(ArticleTopicController, topics)
            save_elements(ArticleImageController, images)
            save_elements(ArticleMediaController, medias)
            save_elements(ArticleHyperlinkController, hyperlinks)
            save_elements(ArticleCategoryController, categories)

    DatabaseManager.close_connection()
    browser.get(r'https://www.google.com.br')
    browser.close()
