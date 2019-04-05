""" Mizu - items.py

/items
/items/price
/items/name

CRUD for Items
"""

from flask import Blueprint, jsonify, request

from mizu.models import Machine
from mizu.models import Slot
from mizu.models import Item

from sqlalchemy import orm

from mizu import db

from mizu.auth import check_token
from mizu.errors import bad_params, bad_headers_content_type

items_bp = Blueprint('items_bp', __name__)


@items_bp.route('/items', methods=['GET'])
@check_token()
def get_items():
    # Query for all items
    items = db.session.query(Item).all()
    items = [{'id': item.id, 'name': item.name, 'price': item.price} for item in items]
    success = {
        'message': 'Retrieved {} items'.format(len(items)),
        'items': items
    }
    return jsonify(success), 200


@items_bp.route('/items', methods=['POST', 'DELETE'])
@check_token(admin_only=True)
def manage_items():
    """ Route for retrieving, creating, and deleting items."""
    if request.method == 'POST':
        # Check headers
        if request.headers.get('Content-Type') != 'application/json':
            return bad_headers_content_type()
        body = request.json

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
                raise ValueError();
        except ValueError:
            return bad_params('You cannot create a worthless item')

        name = body['name']

        new_item = Item(name=name, price=price)
        db.session.add(new_item)
        db.session.commit()

        success = {
            'message': 'Item \'{}\' added succesfully at a price of {} credits'.format(new_item.name, new_item.price)
        }

        return jsonify(success), 201
    elif request.method == 'DELETE':
        if request.headers.get('Content-Type') != 'application/json':
            return bad_headers_content_type();

        body = request.json

        if 'id' not in body:
            return bad_params('An Item ID must be provided for deletion')

        try:
            item_id = int(body['id'])
            if item_id < 0:
                raise ValueError()
            item = db.session.query(Item).filter(Item.id == item_id).first()
            if item is None:
                raise ValueError()
        except ValueError:
            return bad_params('Item ID value provided was invalid, ensure that the ID being provided is attached to an '
                              'item that is present in the system.')

        db.session.delete(item)
        db.session.commit()

        success = {
            'message': 'Item \'{}\' with ID {} successfully deleted'.format(item.name, item.id)
        }
        return jsonify(success), 200


@items_bp.route('/items/price', methods=['PUT'])
@check_token(admin_only=True)
def update_item_price():
    if request.headers.get('Content-Type') != 'application/json':
        return bad_headers_content_type();

    body = request.json

    unprovided = []
    if 'id' not in body:
        unprovided.append('id')
    if 'price' not in body:
        unprovided.append('price')

    if len(unprovided) > 0:
        return bad_params('The following required parameters were not provided: {}'.format(', '.join(unprovided)))

    try:
        price = int(body['price'])
        if price < 0:
            raise ValueError()
    except ValueError:
        return bad_params('You cannot create a worthless item')

    try:
        item_id = int(body['id'])
        if item_id < 0:
            raise ValueError()
        item = db.session.query(Item).filter(Item.id == item_id).\
                  update({"price": price},synchronize_session=False)
        if item < 1:
            raise ValueError()
    except ValueError:
        return bad_params('Item ID value provided was invalid, ensure that the ID being provided is attached to an '
                          'item that is present in the system.')

    db.session.commit()

    item = db.session.query(Item).filter(Item.id == item_id).first()

    success = {
        'message': 'Item \'{}\' with ID {} updated to price {}'.format(item.name, item.id, item.price)
    }
    return jsonify(success), 200

@items_bp.route('/items/name', methods=['PUT'])
@check_token(admin_only=True)
def update_item_name():
    if request.headers.get('Content-Type') != 'application/json':
        return bad_headers_content_type();

    body = request.json

    unprovided = []
    if 'id' not in body:
        unprovided.append('id')
    if 'name' not in body:
        unprovided.append('name')

    if len(unprovided) > 0:
        return bad_params('The following required parameters were not provided: {}'.format(', '.join(unprovided)))

    if body['name'] == '':
        return bad_params('An item cannot have an empty name')

    try:
        item_id = int(body['id'])
        if item_id < 0:
            raise ValueError()
        item = db.session.query(Item).filter(Item.id == item_id).first()
        if item is None:
            raise ValueError
        old_name = item.name
        item = db.session.query(Item).filter(Item.id == item_id).\
                  update({'name': body['name']}, synchronize_session=False)
    except ValueError:
        return bad_params('Item ID value provided was invalid, ensure that the ID being provided is attached to an '
                          'item that is present in the system.')

    db.session.commit()

    item = db.session.query(Item).filter(Item.id == item_id).first()

    success = {
        'message': 'Item with ID {} renamed from \'{}\' to \'{}\''.format(item.id, old_name, item.name)
    }

    return jsonify(success), 200

