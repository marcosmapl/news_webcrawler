# -*- coding: utf-8 -*-
from crawler import AcriticaCrawler
from database import DatabaseManager
from model import AcriticaParser

if __name__ == '__main__':
    # DatabaseManager.create_database(DatabaseManager.POSTGRESQL_DB)

    news_links = AcriticaCrawler.find_news(['haitianos'])
    articles = AcriticaCrawler.get_articles(news_links)
    # properties_name = set()
    for art in articles:
        article = AcriticaParser.parse_article(art)
        print(article)
            # properties_name.add(key)
        print('\n')
    # print(properties_name)