import logging
import os
from datetime import datetime


class Logger:

    __path = os.path.join(os.getcwd(), 'logs')
    __news_logger = None

    @staticmethod
    def configure():
        logging.basicConfig(level=logging.INFO)

        if not os.path.exists(Logger.__path):
            os.mkdir(Logger.__path)

        formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(name)s]:\n\t%(message)s')
        data_hoje = datetime.now().strftime("%Y%m%d_%H%M%S")

        if not Logger.__news_logger:
            Logger.__news_logger = logging.getLogger('news_logger')

            ifh = logging.FileHandler(os.path.join(Logger.__path, f'{data_hoje}_info.log'))
            ifh.setLevel(level=logging.INFO)
            ifh.setFormatter(formatter)
            Logger.__news_logger.addHandler(ifh)

            wfh = logging.FileHandler(os.path.join(Logger.__path, f'{data_hoje}_warn.log'))
            wfh.setLevel(level=logging.WARNING)
            wfh.setFormatter(formatter)
            Logger.__news_logger.addHandler(wfh)

            efh = logging.FileHandler(os.path.join(Logger.__path, f'{data_hoje}_error.log'))
            efh.setLevel(level=logging.ERROR)
            efh.setFormatter(formatter)
            Logger.__news_logger.addHandler(efh)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(level=logging.INFO)
            console_handler.setFormatter(formatter)
            Logger.__news_logger.addHandler(console_handler)

    @staticmethod
    def info(msg: str):
        Logger.__news_logger.info(msg)

    @staticmethod
    def warn(msg: str):
        Logger.__news_logger.warning(msg)

    @staticmethod
    def error(msg: str):
        Logger.__news_logger.error(msg, exc_info=True)
