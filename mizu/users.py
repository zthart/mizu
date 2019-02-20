""" Mizu - users.py

/users
/users/credits

Routes for retrieving users and their credits, and updating drink credits for users
"""

from flask import Blueprint, jsonify, request

from mizu import db

users_bp = Blueprint('users_bp', __name__)

@users_bp.route('/users/', methods=['GET'])
def list_users():
    pass

@users_bp.route('/users/credits', methods=['GET', 'POST'])
def manage_credits():
    pass

