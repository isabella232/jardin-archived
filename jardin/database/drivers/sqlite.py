import sqlite3
from memoized_property import memoized_property

from jardin.database.base import BaseConnection
from jardin.database.lexicon import BaseLexicon


class Lexicon(BaseLexicon):

    @staticmethod
    def table_schema_query(table_name):
        return "pragma table_info(%s);" % table_name

    @staticmethod
    def column_info(row):
        return row['name'], row['dflt_value'], row['type']

    @staticmethod
    def extrapolator(field):
        return ':%s' % field

    @staticmethod
    def row_ids(cursor, primary_key):
        return [cursor.lastrowid]


class DatabaseConnection(BaseConnection):

    DRIVER = sqlite3
    LEXICON = Lexicon

    @memoized_property
    def connect_args(self):
        return [self.db_config.database]

    @memoized_property
    def connect_kwargs(self):
        return {'isolation_level': None}  # autocommit is enabled by setting isolation_level to None

    def execute(self, *query, write=False, **kwargs):
        return super().execute(*query, write=write, **kwargs)
