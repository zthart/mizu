""" Mizu - items.py

/items
/items/price
/items/name

CRUD for Items
"""

from flask import Blueprint, jsonify, request

from mizu import logger

from mizu.auth import check_token
from mizu.data_adapters import get_adapter

from mizu.errors import bad_params, bad_headers_content_type

items_bp = Blueprint('items_bp', __name__)


@items_bp.route('/items', methods=['GET'])
@get_adapter
@check_token()
def get_items(adapter):
    """ Query for all items """

    try:
        items = adapter.get_items()
    except ValueError as e:
        error = {
            'message': str(e),
            'errorCode': 404,
        }

        return jsonify(error), 404

    success = {
        'message': 'Retrieved {} items'.format(len(items)),
        'items': items
    }
    return jsonify(success), 200


@items_bp.route('/items', methods=['POST', 'PUT', 'DELETE'])
@get_adapter
@check_token(admin_only=True)
def manage_items(adapter): # pylint: disable=too-many-return-statements,inconsistent-return-statements
    """ Route for retrieving, creating, and deleting items.

    TODO: Debatably should be split up, should be a simple first issue
    """
    if request.method == 'POST': # pylint: disable=no-else-return
        # Check headers
        if request.headers.get('Content-Type') != 'application/json':
            return bad_headers_content_type()
        body = request.json

        logger.debug('Handling item creation')

        # Keep a list of unprovided params, makes our response nice and clear
        unprovided = []
        if 'name' not in body:
            unprovided.append('name')
        if 'price' not in body:
            unprovided.append('price')

        if len(unprovided) > 0:
            return bad_params('The following required prameters were not provided: {}'.format(', '.join(unprovided)))

        try:
            price = int(body['price'])
            if price < 0:
                raise ValueError()
        except ValueError:
            return bad_params('You cannot create a worthless item')

        logger.debug('Item details validated')

        name = body['name']

        new_item = adapter.create_item(name, price)

        success = {
            'message': 'Item \'{}\' added succesfully at a price of {} credits'.format(
                new_item['name'],
                new_item['price'])
        }

        return jsonify(success), 201
    elif request.method == 'DELETE':
        if request.headers.get('Content-Type') != 'application/json':
            return bad_headers_content_type()

        body = request.json

        logger.debug('Handling item deletion')

        if 'id' not in body:
            return bad_params('An Item ID must be provided for deletion')

        try:
            item_id = int(body['id'])
            if item_id < 0:
                raise ValueError()
            item = adapter.get_item(item_id)
            if item is None:
                raise ValueError()
        except ValueError:
            return bad_params('Item ID value provided was invalid, ensure that the ID being provided is attached to an '
                              'item that is present in the system.')

        logger.debug('Item details validated')

        adapter.delete_item(item['id'])

        success = {
            'message': 'Item \'{}\' with ID {} successfully deleted'.format(item['name'], item['id'])
        }
        return jsonify(success), 200
    elif request.method == 'PUT':
        if request.headers.get('Content-Type') != 'application/json':
            return bad_headers_content_type()

        body = request.json
        price = None
        name = None

        logger.debug('Handling item update')

        if 'id' not in body:
            return bad_params('An Item ID must be provided to update')

        if 'price' not in body and 'name' not in body:
            return bad_params('The name, price, or both values of an item must be provided to update')

        if 'price' in body:
            try:
                price = int(body['price'])
                if price < 0:
                    raise ValueError()
            except ValueError:
                return bad_params('You cannot create a worthless item')

        if 'name' in body:
            name = body['name']
            if name == '':
                return bad_params('An item cannot have an empty name')

        logger.debug('New item details validated')

        try:
            item_id = int(body['id'])
            if item_id < 0:
                raise ValueError()
            item = adapter.get_item(item_id)
            if item is None:
                raise ValueError()

            old_name = item['name']
            old_price = item['price']

            item = adapter.update_item(item_id, name, price)
            print(item)
        except ValueError:
            return bad_params('Item ID value provided was invalid, ensure that the ID being provided is attached to an '
                              'item that is present in the system.')

        logger.debug('Existing item validated for update')

        item = adapter.get_item(item_id)

        success = {
            'message': 'Item ID {} was \'{}\' for {} credits, now \'{}\' for {} credits'.format(
                item['id'], old_name, old_price, item['name'], item['price']
            ),
            'item': item
        }
        return jsonify(success), 200
