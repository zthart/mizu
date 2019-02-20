""" errors.py

Utility file holding some errors that are thrown at least more than once

"""

from flask import jsonify


_bad_headers = {
    'error' : '400 Bad Request - Please ensure that the request contains valid headers',
    'errorCode': 400
}

_bad_params = {
    'error' : '400 Bad Request - Please ensure that the request parameters are valid, and all required parameters are'
              'provided',
    'errorCode': 400,
}

def bad_headers(message='Ensure that your request has valid headers'):
    response = _bad_headers
    response['message'] = message
    return jsonify(response), 400

def bad_params(message='Ensure that your parameters are valid, and all required parameters are provided'):
    response = _bad_params
    response['message'] = message
    return jsonify(response), 400

