from functools import wraps
from flask import request, jsonify

import requests


def check_token(admin_only=False, return_user_obj=False):

    def decorator(func):
        @wraps(func)
        def wrapped_function(*args, **kwargs):

            unauthorized = {
                "error": "Could not authenticate user",
                "errorCode": 401
            }
            permissions = {
                "error": "User does not have the correct permissions",
                "errorCode": 401
            }
            token = request.headers.get('Authorization', None)
            if token is None:
                return jsonify(unauthorized), 401

            headers = {
                "Authorization": token
            }

            endpoint = 'https://sso.csh.rit.edu/auth/realms/csh/protocol/openid-connect/userinfo'

            verify_response = requests.get(endpoint, headers=headers)

            try:
                verify_response.raise_for_status()
            except requests.exceptions.HTTPError:
                return jsonify(unauthorized), 401
            
            verify_body = verify_response.json()


            if admin_only:
                if not 'drink' in verify_body['groups']:
                    return jsonify(permissions), 401

            if return_user_obj:
                return func(*args, user=verify_body, **kwargs)

            return func(*args, **kwargs)
        return wrapped_function
    return decorator

