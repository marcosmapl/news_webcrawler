# -*- coding: utf-8 -*-
from datetime import datetime

from database import DatabaseManager
from logs import Logger
from scraper import PortalAmazoniaScraper, AcriticaScraper

scrapers = [
    AcriticaScraper('acritica', 3),
    PortalAmazoniaScraper('portal_amazonia', 3)
]


if __name__ == '__main__':
    start_time = datetime.now()
    Logger.configure()
    Logger.info(f"COLETA INICIADA EM {start_time}")

    Logger.info(f"CRIANDO A BASE DE DADOS")
    DatabaseManager.create_database(DatabaseManager.POSTGRESQL_DB)

    search_terms = input('DIGITE UM OU MAIS TERMOS DE BUSCA SEPARADOS POR VIRGULA: ').split(',')

    for scraper in scrapers:
        Logger.info(f"INICIANDO COLETA COM O SCRAPER: {scraper.get_scrapper_name()}")
        scraper.start(search_terms)

    Logger.info(f"ENCERRANDO CONEXAO COM A BASE DE DADOS")
    DatabaseManager.close_connection()

    elapsed_time = datetime.now() - start_time
    Logger.info(f'TIME ELAPSED: {elapsed_time}')
    Logger.info('COLETA ENCERRADA!')
