""" Mizu - items.py

/items
/items/price
/items/name

CRUD for Items
"""

from flask import Blueprint, jsonify, request

from mizu import db

items_bp = Blueprint('items_bp', __name__)

