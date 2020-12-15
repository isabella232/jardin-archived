import pymysql

from jardin.tools import retry
from jardin.database.base import BaseClient
from jardin.database.lexicon import BaseLexicon


class Lexicon(BaseLexicon):

    @staticmethod
    def table_schema_query(table_name):
        return "SHOW COLUMNS FROM %s;" % table_name

    @staticmethod
    def column_info(row):
        return row['Field'], row['Default'], row['Type']

    @staticmethod
    def row_ids(cursor, primary_key):
        cursor.execute('SELECT LAST_INSERT_ID();')
        return [cursor.fetchall()[0][0]]

    @staticmethod
    def apply_watermark(query, watermark):
        return ' '.join([watermark, query])


class DatabaseClient(BaseClient):

    lexicon = Lexicon

    @retry(pymysql.OperationalError, tries=3)
    def connect_impl(self, **default_kwargs):
        kwargs = default_kwargs.copy()
        kwargs.update(autocommit=True)
        return pymysql.connect(**kwargs)

    @retry(pymysql.InterfaceError, tries=3)
    def execute_impl(self, conn, *query):
        cursor = conn.cursor()
        cursor.execute(*query)
        return cursor