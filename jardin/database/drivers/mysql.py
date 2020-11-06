import sys
if sys.version_info[0] < 3:
    import MySQLdb
else:
    import pymysql as MySQLdb

from jardin.tools import retry
from jardin.database.base import BaseConnection
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


class DatabaseConnection(BaseConnection):

    DRIVER = MySQLdb
    LEXICON = Lexicon

    @retry(DRIVER.OperationalError, tries=3)
    def connect(self):
        return super(DatabaseConnection, self).connect()

    @retry(DRIVER.InterfaceError, tries=3)
    def execute(self, *query, **kwargs):
        return super(DatabaseConnection, self).execute(*query, **kwargs)
