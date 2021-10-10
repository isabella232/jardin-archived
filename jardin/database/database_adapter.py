import pandas
import time

from jardin import config as config
from jardin.database.base_client import BaseClient
from jardin.query_builders import \
    SelectQueryBuilder, \
    InsertQueryBuilder, \
    UpdateQueryBuilder, \
    DeleteQueryBuilder, \
    RawQueryBuilder
from jardin.cache_stores import cached

MAX_RETRIES = 3

def set_defaults(func):
    def wrapper(self, *args, **kwargs):
        kwargs.update(
            model_metadata=self.model_metadata,
            scheme=self.client_provider.config().scheme,
            lexicon=self.client_provider.lexicon()
            )
        return func(self, *args, **kwargs)
    return wrapper


class DatabaseAdapter(object):

    def __init__(self, client_provider, model_metadata):
        self.client_provider = client_provider
        self.model_metadata = model_metadata

    @set_defaults
    def select(self, **kwargs):
        query = SelectQueryBuilder(**kwargs).query
        config.logger.debug(query)
        results, columns = self._execute(*query, write=False)
        if results is None and columns is None:
            return None
        return pandas.DataFrame.from_records(results, columns=columns, coerce_float=True)

    @set_defaults
    def write(self, query_builder, **kwargs):
        query = query_builder(**kwargs).query
        config.logger.debug(query)
        returning_ids = self._execute(*query, write=True, **kwargs)
        if len(returning_ids) > 0:
            return self.select(where={kwargs['primary_key']: returning_ids})
        return None

    def insert(self, **kwargs):
        return self.write(InsertQueryBuilder, **kwargs)

    def update(self, **kwargs):
        return self.write(UpdateQueryBuilder, **kwargs)

    @set_defaults
    def delete(self, **kwargs):
        query = DeleteQueryBuilder(**kwargs).query
        config.logger.debug(query)
        self._execute(*query, write=False)

    @set_defaults
    @cached
    def raw_query(self, **kwargs):
        query = RawQueryBuilder(**kwargs).query
        config.logger.debug(query)
        results, columns = self._execute(*query, write=False)
        if results is None and columns is None:
            return None
        return pandas.DataFrame.from_records(results, columns=columns, coerce_float=True)

    def _execute(self, *query, **kwargs):
      last_exception = None
      while True:
        current_client = self.client_provider.next_client()
        if current_client is None:
            raise last_exception

        backoff = 0
        for _ in range(MAX_RETRIES):
          try:
              return current_client.execute(*query, **kwargs)
          except current_client.retryable_exceptions as e:
              time.sleep(backoff)
              backoff *= 2
              last_exception = e
              continue
        else:
          if last_exception.__class__ in current_client.connectivity_exceptions:
              current_client.ban(1) # ban connection for one second and try again with a different connection
