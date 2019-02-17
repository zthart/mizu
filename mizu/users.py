""" Mizu - users.py

/users
/users/credits

Routes for retrieving users and their credits, and updating drink credits for users
"""

from flask import Blueprint, jsonify, request

from mizu import db

users_bp = Blueprint('users_bp', __name__)

