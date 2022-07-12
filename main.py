# -*- coding: utf-8 -*-
from crawler import AcriticaCrawler
from database import DatabaseManager, ArticleController
from model import AcriticaParser


search_words = [
    'HAITIANO',
    'HAITIANOS'
    # 'HAITIANA',
    # 'HAITIANAS',
    # 'HAITI'
    # 'VENEZUELANO',
    # 'VENEZUELANOS',
    # 'VENEZUELANA',
    # 'VENEZUELANAS'
    # 'VENEZUELA'
]
if __name__ == '__main__':
    DatabaseManager.create_database(DatabaseManager.POSTGRESQL_DB)

    db_links = [x.article_url for x in ArticleController.fetch_all()]
    news_links = AcriticaCrawler.find_news(search_words)
    articles = AcriticaCrawler.get_articles([x for x in news_links if str(x) not in db_links])

    for art in articles:
        print(art)
        print('\n')

    try:
        ArticleController.insert_batch(articles)
    except Exception as err:
        print(err)
