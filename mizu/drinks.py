""" Mizu - drinks.py

/drinks
/drinks/drop

Routes for retrieving information on the contents of the machines, and dropping drinks
"""

from flask import Blueprint, jsonify, request

from mizu import db

drinks_bp = Blueprint('drinks_bp', __name__)

@drinks_bp.route('/drinks/', methods=['GET'])
def current_drinks():
    pass

@drinks_bp.route('/drinks/drop', methods=['POST'])
def drop_drink():
    pass

