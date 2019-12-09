""" Storage Interface Decorator

A function decorator for use in functions that require access to a storage backend that returns the proper backend for
the request type.
"""
from functools import wraps
from flask import request

from mizu.data_adapters import SqlAlchemyAdapter
from mizu.data_adapters import MockAdapter

def get_adapter(func):
    """ Inspect the incoming request and determine which storage adapter to return """
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        mock = request.args.get('mock', False)
        if isinstance(mock, str):
            mock = mock.lower().startswith('t')

        if mock:
            return func(MockAdapter, *args, **kwargs)
        else:
            return func(SqlAlchemyAdapter, *args, **kwargs)
    return wrapped_function
