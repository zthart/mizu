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

from mizu.errors import bad_headers, bad_params

items_bp = Blueprint('items_bp', __name__)


@items_bp.route('/items', methods=['GET', 'POST', 'DELETE'])
def manage_items():
    """ Route for retrieving, creating, and deleting items."""
    if request.method == 'GET':
        # Query for all items
        items = db.session.query(Item).all()
        items = [{'id': item.id, 'name': item.name, 'price': item.price} for item in items]
        success = {
            'message': 'Retrieved {} items'.format(len(items)),
            'items': items
        }
        return jsonify(success), 200
    elif request.method == 'POST':
        # Check headers
        if request.headers.get('Content-Type') != 'application/json':
            return bad_headers('Invalid Content-Type - the body of your request should be \'application/json\'')

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
                raise ValueError('Item price must be positive');
        except ValueError as e:
            return bad_params('Ensure the item price is an integer - {}'.format(e))

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
            return bad_headers('Invalid Content-Type - the body of your request should be \'application/json\'')

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
            

@items_bp.route('/items/price', methods=['POST'])
def update_item_price():
    pass

@items_bp.route('/items/name', methods=['POST'])
def update_item_name():
    pass

