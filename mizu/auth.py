""" User/Machine authentication wrapper

**ALL ENDPOINTS** should be wrapped with this decorator, with the exception of the error handler functions and root
redirect endpoint. Admin-only endpoints should have the ``admin_only`` optional argument provided - trusted client
calls (i.e. calls that provide the machine API token) are allowed access to all endpoints. Mocked requests will still
go through this validation, but will not return unauthorized.
"""
from functools import wraps
from flask import request, jsonify

import requests

from mizu import logger
from mizu import app

def check_token(admin_only=False, return_user_obj=False):
    """ Validate a provided Bearer token against CSH SSO """
    def decorator(func):
        @wraps(func)
        def wrapped_function(*args, **kwargs): # pylint: disable=too-many-return-statements

            logger.debug('Begin handling request for %s', request.host)
            unauthorized = {
                "error": "Could not authenticate user",
                "errorCode": 401
            }
            key_unauthorized = {
                "error": "Unable to authenticate trusted client",
                "errorCode": 401
            }
            permissions = {
                "error": "User does not have the correct permissions",
                "errorCode": 401
            }

            # First, could this be a trusted client?
            key = request.headers.get('X-Auth-Token', None)
            if key is not None:
                if key == app.config['MACHINE_API_TOKEN']:
                    return func(*args, **kwargs)
                return jsonify(key_unauthorized), 401

            # Otherwise, validate JWT against SSO
            token = request.headers.get('Authorization', None)
            if token is None:
                logger.debug('User unauthorized with no Bearer token')
                return jsonify(unauthorized), 401

            headers = {
                "Authorization": token
            }

            endpoint = 'https://sso.csh.rit.edu/auth/realms/csh/protocol/openid-connect/userinfo'

            verify_response = requests.get(endpoint, headers=headers)

            try:
                verify_response.raise_for_status()
            except requests.exceptions.HTTPError:
                logger.debug('Unable to verify Bearer token against provider')
                return jsonify(unauthorized), 401

            verify_body = verify_response.json()

            mock = request.args.get('mock', False)
            if isinstance(mock, str):
                mock = mock.lower().startswith('t')

            if admin_only and not mock:
                if not 'drink' in verify_body['groups']:
                    return jsonify(permissions), 401

            logger.debug('Successfully authenticated user %s', verify_body['preferred_username'])
            if return_user_obj:
                return func(*args, user=verify_body, **kwargs)

            return func(*args, **kwargs)
        return wrapped_function
    return decorator
