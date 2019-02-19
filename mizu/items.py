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

from mizu import db

items_bp = Blueprint('items_bp', __name__)


@items_bp.route('/items', methods=['GET', 'POST', 'DELETE'])
def manage_items():
    pass

@items_bd.route('/items/price', methods=['POST'])
def update_item_price():
    pass

@items_db.route('/items/name', methods=['POST'])
def update_item_name():
    pass

