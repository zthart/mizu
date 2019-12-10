from functools import wraps
from flask import request

from mizu.data_adapters import SqlAlchemyAdapter
from mizu.data_adapters import MockAdapter

def get_adapter(func):
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

