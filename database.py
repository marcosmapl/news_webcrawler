# -*- coding: utf-8 -*-
from configparser import ConfigParser
from typing import List

import psycopg2
import os

from psycopg2 import extras

from model import Article, ArticleImage, ArticleTopic, ArticleMedia, ArticleHyperlink, ArticleCategory


class DatabaseManager:
    """
    Classe responsável pela criação do banco de dados e gerenciamento das conexões com o SGBD.

    As conexões com o SGBD seguem o pattern Singleton.

    Constants:
        - POSTGRESQL_DB (str): String constante com o nome do SGBD postgresql, para uso na requisição de uma conexão.
        - DATABASE_NAME (str): String constante com o nome do banco de dados utilizado nesta aplicação.

    """

    POSTGRESQL_DB = 'postgresql'
    DATABASE_NAME = 'news'
    __db_config_filename = 'database.ini' # nome do arquivo de configurações da conexão com o sgbd
    __connection = None # objeto singleton de conexão com o sgbd

    @classmethod
    def __get_connection_params(cls, sgbd_name: str):
        """
        Esta função carrega os parametros de conexão do arquivo de configurações e coloca-os num dicionário.

        Args:
            sgbd_name (str): Nome do SGDB a ser utilizado (POSTGRESQL_DB).

        Raises:
            FileNotFoundError: Caso o arquivo de configurações não seja encontrado na pasta atual.
            Exception: Caso a seção para o SGBD escolhido não sejam encontradas no arquivo de configurações.
        """
        # verifica se o arquivo de configurações existe
        if os.path.exists(DatabaseManager.__db_config_filename):
            # criar um objeto parser e carrega o arquivo de configurações
            parser = ConfigParser()
            parser.read(DatabaseManager.__db_config_filename)
            # se a seção escolhida (sgbd) estiver presente no arquivo, carrega os parametros para um dicionário
            if parser.has_section(sgbd_name):
                params = parser.items(sgbd_name)
                db = dict(params)
                return db
            else:
                raise Exception(f'Section {sgbd_name} not found in the {DatabaseManager.__db_config_filename} file')
        else:
            raise FileNotFoundError(f'O arquivo {DatabaseManager.__db_config_filename} de configurações para o sgbd {sgbd_name} não foi encontrado!')

    @classmethod
    def get_connection(cls, sgbd_name: str):
        """
        Esta função é responsável por fonecer o objeto Singleton de conexão com o SGBD.

        Caso o objeto de conexão não exista ou a conexão estiver fechada, abre uma nova conexão num novo objeto.

        Args:
            sgbd_name (str): Nome do SGDB a ser utilizado (POSTGRESQL_DB | MYSQL_DB).
        """
        if not DatabaseManager.__connection or DatabaseManager.__connection.closed:
            DatabaseManager.__connection = psycopg2.connect(**DatabaseManager.__get_connection_params(sgbd_name))
        return DatabaseManager.__connection

    @classmethod
    def close_connection(cls):
        """
        Esta função é responsável por fechar a conexão ativa com o SGBD.

        Caso o objeto de conexão não exista ou a conexão estiver fechada, abre uma nova conexão num novo objeto.

        Args:
            sgbd_name (str): Nome do SGDB a ser utilizado (POSTGRESQL_DB | MYSQL_DB).
        """
        if DatabaseManager.__connection and not DatabaseManager.__connection.closed:
            DatabaseManager.__connection.close()

    @classmethod
    def create_database(cls, sgbd_name: str):
        """
        Esta função é responsável por estabelecer a primeira conexão com o SGBD, criar o schema do banco de dados, tabelas e relacionamentos.

        A primeira conexão feita é para criar o schema do banco de dados, por isso conectamos diretamente no banco de dados padrão do sgbd.

        Args:
            sgbd_name (str): Nome do SGDB a ser utilizado (POSTGRESQL_DB | MYSQL_DB).
        """
        # db_params = DatabaseManager.__get_connection_params(sgbd_name)
        # db_params['database'] = 'postgres'
        # conn = psycopg2.connect(db_params)
        # conn.autocommit = True
        # cursor = conn.cursor()
        # cursor.execute(f"CREATE DATABASE {sgbd_name}")
        # conn.close()
        # lê e executa o script de criação das tabelas do banco de dados
        with open('create_tables.sql', 'r') as db_file:
            sql = ''.join(db_file.readlines())
            conn = DatabaseManager.get_connection(sgbd_name)
            cursor = conn.cursor()
            cursor.execute(sql)
            cursor.close()
            conn.commit()
            conn.close()


class ModelController:
    """Classe controller que implementa as funções de CRUD de objetos no banco de dados"""

    @classmethod
    def _insert_one(cls, row, table_name: str, attr_list):
        """
        Esta função recebe um registro (tupla) e o insere na respectiva tabela do banco de dados.

        :param row: Uma tupla de valores (registro) a serem inseridos na tabela
        :param table_name: Nome da tabela
        :param attr_list: Uma lista com os nomes dos respectivos atributos (campos da tabela) cujos valores estão no registro.
        :return:
        """
        # constroi o comando SQL para inserção do registro na tabela
        fields = ', '.join(attr_list)
        params = ', '.join(['%s' for _ in attr_list])
        query = f"INSERT INTO {table_name} ({fields}) VALUES ({params})"
        # recupera a conexão com o sgbd
        connection = DatabaseManager.get_connection(DatabaseManager.POSTGRESQL_DB)
        cursor = connection.cursor()
        # executa o comando SQL
        cursor.execute(query, row)
        connection.commit()
        return cursor.rowcount

    @classmethod
    def _insert_many(cls, rows, table_name: str, attr_list):
        """
        Esta função recebe registros (tuplas) e os insere na respectiva tabela do banco de dados.

        :param rows: As tuplas de valores (registros) a serem inseridos na tabela
        :param table_name: Nome da tabela
        :param attr_list: Uma lista com os nomes dos respectivos atributos (campos da tabela) cujos valores estão no registro.
        :return:
        """
        # constroi o comando SQL para inserção do registro na tabela
        attr_names = ','.join(attr_list)
        sql_query = f'INSERT INTO {table_name} ({attr_names}) VALUES %s'
        # recupera a conexão com o sgbd
        connection = DatabaseManager.get_connection(DatabaseManager.POSTGRESQL_DB)
        cursor = connection.cursor()
        # executa o comando SQL
        extras.execute_values(cursor, sql_query, rows)
        connection.commit()
        return cursor.rowcount

    @classmethod
    def _fetch_all(cls, table_name: str):
        """
        Esta função recupera todos os registros de uma dada tabela do banco de dados.

        :param table_name: Nome da tabela do banco de dados.
        :return: Os registros (tuplas) encontrados na tabela.
        """
        connection = DatabaseManager.get_connection(DatabaseManager.POSTGRESQL_DB)
        cursor = connection.cursor()
        cursor.execute(f'SELECT * FROM {table_name}')
        return cursor.fetchall()

    @classmethod
    def _fetch_by_text_field(cls, table_name: str, field_value: str, field_name: str, exact=True, limit=None):
        """
        Esta função recupera registros (tuplas) de uma tabela do banco de dados por meio de uma busca pelo valor textual de um compo informado.

        :param table_name: Nome da tabela do banco de dados.
        :param field_value: Valor do campo a ser utilizado na busca.
        :param field_name: Nome do compo da tabela.
        :param exact: Booleano que indica se a busca deve ser pelo valor exato ou não.
        :param limit: Limite de registros a serem retornados. Caso seja "None", todos os registros encontrados serão retornados.
        :return: Os registros (tuplas) encontrados pela busca.
        """
        params = [field_value]
        if limit:
            params.append(limit)
        connection = DatabaseManager.get_connection(DatabaseManager.POSTGRESQL_DB)
        rows = connection.query(
            f'SELECT * FROM {table_name} WHERE {field_name} {"LIKE %s" if not exact else "= %s"}{"" if not limit else " LIMIT %s"}',
            tuple(params)
        )
        return rows

    @classmethod
    def _fetch_by_numerical_field(cls, table_name: str, field_value: int, field_name: str, limit=None):
        """
         Esta função recupera registros (tuplas) de uma tabela do banco de dados por meio de uma busca pelo valor inteiro de um compo informado.

        :param table_name: Nome da tabela do banco de dados.
        :param field_value: Valor do campo a ser utilizado na busca.
        :param field_name: Nome do compo da tabela.
        :param limit: Limite de registros a serem retornados. Caso seja "None", todos os registros encontrados serão retornados.
        :return: Os registros (tuplas) encontrados pela busca.
        """
        params = [field_value]
        if limit:
            params.append(limit)
        return DatabaseManager.get_connection(DatabaseManager.POSTGRESQL_DB).query(
            f'SELECT * FROM {table_name}{f" WHERE {field_name}=%s"}{"" if not limit else " LIMIT %s"}',
            tuple(params)
        )


class ArticleController(ModelController):
    """Classe que implementa as funções de CRUD para objetos `Article`."""
    __TABLE_NAME = 'article'

    @classmethod
    def insert_one(cls, element: Article):
        """
        Esta função insere um novo registro na tabela `article` com o valores provenientes de um objeto `Article`.

        :param element: O objeto `Article` cujos valores deverão ser inseridos.
        :return: Um inteiro maior que `zero` se registro foi inserido com sucesso.
        """
        return ModelController._insert_one(element.to_tuple(), cls.__TABLE_NAME, Article.attr_list())

    @classmethod
    def insert_batch(cls, elements: List[Article]):
        """
        Esta função insere novos registros na tabela `Article` com os valores provenientes de uma lista de objetos `Article`.

        :param elements: A lista com os objetos `Article` cujos valores deverão ser inseridos como novos registros da tabela.
        :return: Um inteiro maior que `zero` se registros foram inseridos com sucesso.
        """
        return ModelController._insert_many([x.to_tuple() for x in elements], cls.__TABLE_NAME, Article.attr_list())

    @classmethod
    def fetch_all(cls):
        """
        Esta função recupera todos os registros da tabela `Article` mapeados para uma lista de objetos `Article`.

        :return: Uma lista contendo os registros da tabela, mapeados para objetos `Article`.
        """
        return [Article.from_tuple(x) for x in ModelController._fetch_all(cls.__TABLE_NAME)]

    @classmethod
    def fetch_by_text_field(cls, field_value: str, field_name: str, exact=True, limit=None):
        """
        Esta função recupera uma seleção de registros da tabela `article` por meio de uma busca por um parametro textual num dos campos da tabela.
        Os registros que satisfizerem o critério de busca serão mapeados e retornados numa lista de objetos `Article`.

        :param field_value: O valor textual do campos no registros desejados.
        :param field_name: O nome do campo a ser utilizado na busca.
        :param exact: Booleano que indica se a busca textual deve ser exata ou não.
        :param limit: Inteiro que especifica o número máximo (limite) de registros a serem retornados, caso seja "None" todos os registros encontrados serão retornados.
        :return: Os registros, que satisfizerem o critério de buscar, mapeados num lista de objetos `Article`
        """
        return ModelController._fetch_by_text_field(cls.__TABLE_NAME, field_value, field_name, exact, limit)

    @classmethod
    def fetch_by_numerical_field(cls, field_value: int, field_name: str, limit=None):
        """
        Esta função recupera uma seleção de registros da tabela `product` por meio de uma busca por um parametro inteiro num dos campos da tabela.
        Os registros que satisfizerem o critério de busca serão mapeados e retornados numa lista de objetos `Article`.

        :param field_value: O valor inteiro do campos no registros desejados.
        :param field_name: O nome do campo a ser utilizado na busca.
        :param limit: Inteiro que especifica o número máximo (limite) de registros a serem retornados, caso seja "None" todos os registros encontrados serão retornados.
        :return: Os registros, que satisfizerem o critério de buscar, mapeados num lista de objetos `Article`
        """
        return ModelController._fetch_by_numerical_field(cls.__TABLE_NAME, field_value, field_name, limit)


class ArticleImageController(ModelController):
    """Classe que implementa as funções de CRUD para objetos `ArticleImage`."""
    __TABLE_NAME = 'article_image'

    @classmethod
    def insert_one(cls, element: ArticleImage):
        """
        Esta função insere um novo registro na tabela `article_image` com o valores provenientes de um objeto `ArticleImage`.

        :param element: O objeto `ArticleImage` cujos valores deverão ser inseridos.
        :return: Um inteiro maior que `zero` se registro foi inserido com sucesso.
        """
        return ModelController._insert_one(element.to_tuple(), cls.__TABLE_NAME, ArticleImage.attr_list())

    @classmethod
    def insert_batch(cls, elements: List[ArticleImage]):
        """
        Esta função insere novos registros na tabela `article_image` com os valores provenientes de uma lista de objetos `ArticleImage`.

        :param elements: A lista com os objetos `ArticleImage` cujos valores deverão ser inseridos como novos registros da tabela.
        :return: Um inteiro maior que `zero` se registros foram inseridos com sucesso.
        """
        return ModelController._insert_many([x.to_tuple() for x in elements], cls.__TABLE_NAME, ArticleImage.attr_list())

    @classmethod
    def fetch_all(cls):
        """
        Esta função recupera todos os registros da tabela `article_image` mapeados para uma lista de objetos `ArticleImage`.

        :return: Uma lista contendo os registros da tabela, mapeados para objetos `ArticleImage`.
        """
        return [ArticleImage.from_tuple(x) for x in ModelController._fetch_all(cls.__TABLE_NAME)]

    @classmethod
    def fetch_by_text_field(cls, field_value: str, field_name: str, exact=True, limit=None):
        """
        Esta função recupera uma seleção de registros da tabela `article_image` por meio de uma busca por um parametro textual num dos campos da tabela.
        Os registros que satisfizerem o critério de busca serão mapeados e retornados numa lista de objetos `ArticleImage`.

        :param field_value: O valor textual do campos no registros desejados.
        :param field_name: O nome do campo a ser utilizado na busca.
        :param exact: Booleano que indica se a busca textual deve ser exata ou não.
        :param limit: Inteiro que especifica o número máximo (limite) de registros a serem retornados, caso seja "None" todos os registros encontrados serão retornados.
        :return: Os registros, que satisfizerem o critério de buscar, mapeados num lista de objetos `ArticleImage`
        """
        return ModelController._fetch_by_text_field(cls.__TABLE_NAME, field_value, field_name, exact, limit)

    @classmethod
    def fetch_by_numerical_field(cls, field_value: int, field_name: str, limit=None):
        """
        Esta função recupera uma seleção de registros da tabela `article_image` por meio de uma busca por um parametro inteiro num dos campos da tabela.
        Os registros que satisfizerem o critério de busca serão mapeados e retornados numa lista de objetos `ArticleImage`.

        :param field_value: O valor inteiro do campos no registros desejados.
        :param field_name: O nome do campo a ser utilizado na busca.
        :param limit: Inteiro que especifica o número máximo (limite) de registros a serem retornados, caso seja "None" todos os registros encontrados serão retornados.
        :return: Os registros, que satisfizerem o critério de buscar, mapeados num lista de objetos `ArticleImage`
        """
        return ModelController._fetch_by_numerical_field(cls.__TABLE_NAME, field_value, field_name, limit)


class ArticleTopicController(ModelController):
    """Classe que implementa as funções de CRUD para objetos `ArticleTopic`."""
    __TABLE_NAME = 'article_topic'

    @classmethod
    def insert_one(cls, element: ArticleTopic):
        """
        Esta função insere um novo registro na tabela `article_topic` com o valores provenientes de um objeto `ArticleTopic`.

        :param element: O objeto `ArticleTopic` cujos valores deverão ser inseridos.
        :return: Um inteiro maior que `zero` se registro foi inserido com sucesso.
        """
        return ModelController._insert_one(element.to_tuple(), cls.__TABLE_NAME, ArticleTopic.attr_list())

    @classmethod
    def insert_batch(cls, elements: List[ArticleTopic]):
        """
        Esta função insere novos registros na tabela `article_topic` com os valores provenientes de uma lista de objetos `ArticleTopic`.

        :param elements: A lista com os objetos `ArticleTopic` cujos valores deverão ser inseridos como novos registros da tabela.
        :return: Um inteiro maior que `zero` se registros foram inseridos com sucesso.
        """
        return ModelController._insert_many([x.to_tuple() for x in elements], cls.__TABLE_NAME, ArticleTopic.attr_list())

    @classmethod
    def fetch_all(cls):
        """
        Esta função recupera todos os registros da tabela `article_topic` mapeados para uma lista de objetos `ArticleTopic`.

        :return: Uma lista contendo os registros da tabela, mapeados para objetos `ArticleTopic`.
        """
        return [ArticleTopic.from_tuple(x) for x in ModelController._fetch_all(cls.__TABLE_NAME)]

    @classmethod
    def fetch_by_text_field(cls, field_value: str, field_name: str, exact=True, limit=None):
        """
        Esta função recupera uma seleção de registros da tabela `article_topic` por meio de uma busca por um parametro textual num dos campos da tabela.
        Os registros que satisfizerem o critério de busca serão mapeados e retornados numa lista de objetos `ArticleTopic`.

        :param field_value: O valor textual do campos no registros desejados.
        :param field_name: O nome do campo a ser utilizado na busca.
        :param exact: Booleano que indica se a busca textual deve ser exata ou não.
        :param limit: Inteiro que especifica o número máximo (limite) de registros a serem retornados, caso seja "None" todos os registros encontrados serão retornados.
        :return: Os registros, que satisfizerem o critério de buscar, mapeados num lista de objetos `ArticleTopic`
        """
        return ModelController._fetch_by_text_field(cls.__TABLE_NAME, field_value, field_name, exact, limit)

    @classmethod
    def fetch_by_numerical_field(cls, field_value: int, field_name: str, limit=None):
        """
        Esta função recupera uma seleção de registros da tabela `article_topic` por meio de uma busca por um parametro inteiro num dos campos da tabela.
        Os registros que satisfizerem o critério de busca serão mapeados e retornados numa lista de objetos `ArticleTopic`.

        :param field_value: O valor inteiro do campos no registros desejados.
        :param field_name: O nome do campo a ser utilizado na busca.
        :param limit: Inteiro que especifica o número máximo (limite) de registros a serem retornados, caso seja "None" todos os registros encontrados serão retornados.
        :return: Os registros, que satisfizerem o critério de buscar, mapeados num lista de objetos `ArticleTopic`
        """
        return ModelController._fetch_by_numerical_field(cls.__TABLE_NAME, field_value, field_name, limit)


class ArticleMediaController(ModelController):
    """Classe que implementa as funções de CRUD para objetos `ArticleMedia`."""
    __TABLE_NAME = 'article_media'

    @classmethod
    def insert_one(cls, element: ArticleMedia):
        """
        Esta função insere um novo registro na tabela `article_media` com o valores provenientes de um objeto `ArticleMedia`.

        :param element: O objeto `ArticleMedia` cujos valores deverão ser inseridos.
        :return: Um inteiro maior que `zero` se registro foi inserido com sucesso.
        """
        return ModelController._insert_one(element.to_tuple(), cls.__TABLE_NAME, ArticleMedia.attr_list())

    @classmethod
    def insert_batch(cls, elements: List[ArticleMedia]):
        """
        Esta função insere novos registros na tabela `article_media` com os valores provenientes de uma lista de objetos `ArticleMedia`.

        :param elements: A lista com os objetos `ArticleMedia` cujos valores deverão ser inseridos como novos registros da tabela.
        :return: Um inteiro maior que `zero` se registros foram inseridos com sucesso.
        """
        return ModelController._insert_many([x.to_tuple() for x in elements], cls.__TABLE_NAME, ArticleMedia.attr_list())

    @classmethod
    def fetch_all(cls):
        """
        Esta função recupera todos os registros da tabela `article_media` mapeados para uma lista de objetos `ArticleMedia`.

        :return: Uma lista contendo os registros da tabela, mapeados para objetos `ArticleMedia`.
        """
        return [ArticleMedia.from_tuple(x) for x in ModelController._fetch_all(cls.__TABLE_NAME)]

    @classmethod
    def fetch_by_text_field(cls, field_value: str, field_name: str, exact=True, limit=None):
        """
        Esta função recupera uma seleção de registros da tabela `article_media` por meio de uma busca por um parametro textual num dos campos da tabela.
        Os registros que satisfizerem o critério de busca serão mapeados e retornados numa lista de objetos `ArticleMedia`.

        :param field_value: O valor textual do campos no registros desejados.
        :param field_name: O nome do campo a ser utilizado na busca.
        :param exact: Booleano que indica se a busca textual deve ser exata ou não.
        :param limit: Inteiro que especifica o número máximo (limite) de registros a serem retornados, caso seja "None" todos os registros encontrados serão retornados.
        :return: Os registros, que satisfizerem o critério de buscar, mapeados num lista de objetos `ArticleMedia`
        """
        return ModelController._fetch_by_text_field(cls.__TABLE_NAME, field_value, field_name, exact, limit)

    @classmethod
    def fetch_by_numerical_field(cls, field_value: int, field_name: str, limit=None):
        """
        Esta função recupera uma seleção de registros da tabela `article_media` por meio de uma busca por um parametro inteiro num dos campos da tabela.
        Os registros que satisfizerem o critério de busca serão mapeados e retornados numa lista de objetos `ArticleMedia`.

        :param field_value: O valor inteiro do campos no registros desejados.
        :param field_name: O nome do campo a ser utilizado na busca.
        :param limit: Inteiro que especifica o número máximo (limite) de registros a serem retornados, caso seja "None" todos os registros encontrados serão retornados.
        :return: Os registros, que satisfizerem o critério de buscar, mapeados num lista de objetos `ArticleMedia`
        """
        return ModelController._fetch_by_numerical_field(cls.__TABLE_NAME, field_value, field_name, limit)


class ArticleHyperlinkController(ModelController):
    """Classe que implementa as funções de CRUD para objetos `ArticleHyperlink`."""
    __TABLE_NAME = 'article_hyperlink'

    @classmethod
    def insert_one(cls, element: ArticleMedia):
        """
        Esta função insere um novo registro na tabela `article_hyperlink` com o valores provenientes de um objeto `ArticleHyperlink`.

        :param element: O objeto `ArticleHyperlink` cujos valores deverão ser inseridos.
        :return: Um inteiro maior que `zero` se registro foi inserido com sucesso.
        """
        return ModelController._insert_one(element.to_tuple(), cls.__TABLE_NAME, ArticleHyperlink.attr_list())

    @classmethod
    def insert_batch(cls, elements: List[ArticleHyperlink]):
        """
        Esta função insere novos registros na tabela `article_hyperlink` com os valores provenientes de uma lista de objetos `ArticleHyperlink`.

        :param elements: A lista com os objetos `ArticleHyperlink` cujos valores deverão ser inseridos como novos registros da tabela.
        :return: Um inteiro maior que `zero` se registros foram inseridos com sucesso.
        """
        return ModelController._insert_many([x.to_tuple() for x in elements], cls.__TABLE_NAME, ArticleHyperlink.attr_list())

    @classmethod
    def fetch_all(cls):
        """
        Esta função recupera todos os registros da tabela `article_hyperlink` mapeados para uma lista de objetos `ArticleHyperlink`.

        :return: Uma lista contendo os registros da tabela, mapeados para objetos `ArticleHyperlink`.
        """
        return [ArticleHyperlink.from_tuple(x) for x in ModelController._fetch_all(cls.__TABLE_NAME)]

    @classmethod
    def fetch_by_text_field(cls, field_value: str, field_name: str, exact=True, limit=None):
        """
        Esta função recupera uma seleção de registros da tabela `article_hyperlink` por meio de uma busca por um parametro textual num dos campos da tabela.
        Os registros que satisfizerem o critério de busca serão mapeados e retornados numa lista de objetos `ArticleHyperlink`.

        :param field_value: O valor textual do campos no registros desejados.
        :param field_name: O nome do campo a ser utilizado na busca.
        :param exact: Booleano que indica se a busca textual deve ser exata ou não.
        :param limit: Inteiro que especifica o número máximo (limite) de registros a serem retornados, caso seja "None" todos os registros encontrados serão retornados.
        :return: Os registros, que satisfizerem o critério de buscar, mapeados num lista de objetos `ArticleHyperlink`
        """
        return ModelController._fetch_by_text_field(cls.__TABLE_NAME, field_value, field_name, exact, limit)

    @classmethod
    def fetch_by_numerical_field(cls, field_value: int, field_name: str, limit=None):
        """
        Esta função recupera uma seleção de registros da tabela `article_hyperlink` por meio de uma busca por um parametro inteiro num dos campos da tabela.
        Os registros que satisfizerem o critério de busca serão mapeados e retornados numa lista de objetos `ArticleHyperlink`.

        :param field_value: O valor inteiro do campos no registros desejados.
        :param field_name: O nome do campo a ser utilizado na busca.
        :param limit: Inteiro que especifica o número máximo (limite) de registros a serem retornados, caso seja "None" todos os registros encontrados serão retornados.
        :return: Os registros, que satisfizerem o critério de buscar, mapeados num lista de objetos `ArticleHyperlink`
        """
        return ModelController._fetch_by_numerical_field(cls.__TABLE_NAME, field_value, field_name, limit)


class ArticleCategoryController(ModelController):
    """Classe que implementa as funções de CRUD para objetos `ArticleCategory`."""
    __TABLE_NAME = 'article_category'

    @classmethod
    def insert_one(cls, element: ArticleCategory):
        """
        Esta função insere um novo registro na tabela `article_category` com o valores provenientes de um objeto `ArticleCategory`.

        :param element: O objeto `ArticleImage` cujos valores deverão ser inseridos.
        :return: Um inteiro maior que `zero` se registro foi inserido com sucesso.
        """
        return ModelController._insert_one(element.to_tuple(), cls.__TABLE_NAME, ArticleCategory.attr_list())

    @classmethod
    def insert_batch(cls, elements: List[ArticleCategory]):
        """
        Esta função insere novos registros na tabela `article_category` com os valores provenientes de uma lista de objetos `ArticleCategory`.

        :param elements: A lista com os objetos `ArticleCategory` cujos valores deverão ser inseridos como novos registros da tabela.
        :return: Um inteiro maior que `zero` se registros foram inseridos com sucesso.
        """
        return ModelController._insert_many([x.to_tuple() for x in elements], cls.__TABLE_NAME, ArticleCategory.attr_list())

    @classmethod
    def fetch_all(cls):
        """
        Esta função recupera todos os registros da tabela `article_category` mapeados para uma lista de objetos `ArticleCategory`.

        :return: Uma lista contendo os registros da tabela, mapeados para objetos `ArticleCategory`.
        """
        return [ArticleCategory.from_tuple(x) for x in ModelController._fetch_all(cls.__TABLE_NAME)]

    @classmethod
    def fetch_by_text_field(cls, field_value: str, field_name: str, exact=True, limit=None):
        """
        Esta função recupera uma seleção de registros da tabela `article_category` por meio de uma busca por um parametro textual num dos campos da tabela.
        Os registros que satisfizerem o critério de busca serão mapeados e retornados numa lista de objetos `ArticleCategory`.

        :param field_value: O valor textual do campos no registros desejados.
        :param field_name: O nome do campo a ser utilizado na busca.
        :param exact: Booleano que indica se a busca textual deve ser exata ou não.
        :param limit: Inteiro que especifica o número máximo (limite) de registros a serem retornados, caso seja "None" todos os registros encontrados serão retornados.
        :return: Os registros, que satisfizerem o critério de buscar, mapeados num lista de objetos `ArticleCategory`
        """
        return ModelController._fetch_by_text_field(cls.__TABLE_NAME, field_value, field_name, exact, limit)

    @classmethod
    def fetch_by_numerical_field(cls, field_value: int, field_name: str, limit=None):
        """
        Esta função recupera uma seleção de registros da tabela `article_category` por meio de uma busca por um parametro inteiro num dos campos da tabela.
        Os registros que satisfizerem o critério de busca serão mapeados e retornados numa lista de objetos `ArticleCategory`.

        :param field_value: O valor inteiro do campos no registros desejados.
        :param field_name: O nome do campo a ser utilizado na busca.
        :param limit: Inteiro que especifica o número máximo (limite) de registros a serem retornados, caso seja "None" todos os registros encontrados serão retornados.
        :return: Os registros, que satisfizerem o critério de buscar, mapeados num lista de objetos `ArticleCategory`
        """
        return ModelController._fetch_by_numerical_field(cls.__TABLE_NAME, field_value, field_name, limit)
