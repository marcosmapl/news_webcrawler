# -*- coding: utf-8 -*-
from crawler import AcriticaCrawler
from database import DatabaseManager, ArticleController
from model import AcriticaParser

if __name__ == '__main__':
    DatabaseManager.create_database(DatabaseManager.POSTGRESQL_DB)
    # db_links = [x.article_url for x in ArticleController.fetch_all()]
    # news_links = AcriticaCrawler.find_news(['haitianos'])
    # articles = AcriticaCrawler.get_articles([x for x in news_links if str(x) not in db_links])
    articles = AcriticaCrawler.get_articles(['/geral/familias-fogem-de-casa-durante-onda-de-violencia-no-haiti-1.268772',
                                             '/manaus/haitiana-vitima-de-perseguic-o-e-roubos-em-manaus-desabafa-me-deixem-trabalhar-em-paz-1.269209'])
    # properties_name = set()
    for art in articles:
        print(art)
        try:
            ArticleController.insert_one(art)
        except Exception as err:
            print(err)
            # properties_name.add(key)
        print('\n')
    # print(properties_name)
