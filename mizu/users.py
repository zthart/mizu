""" Mizu - users.py

/users
/users/credits

Routes for retrieving users and their credits, and updating drink credits for users
"""

from flask import Blueprint, jsonify, request

import ldap
import ldap.modlist

from mizu import db
from mizu import ldap as _ldap

from mizu.auth import check_token
from mizu.errors import bad_params, bad_headers_content_type

users_bp = Blueprint('users_bp', __name__)

@users_bp.route('/users', methods=['GET'])
@check_token()
def list_users():
    # Turns out creating objects for each of our 1200+ users is very slow. Querying LDAP directly is much faster
    ldap_conn = _ldap.get_con()
    users = ldap_conn.search_s("cn=users,cn=accounts,dc=csh,dc=rit,dc=edu",
                               ldap.SCOPE_SUBTREE,
                               "(objectClass=cshMember)",
                               ["uid", "cn", "drinkBalance"])

    users = [{
        'cn': user[1]['cn'][0].decode('utf-8'),
        'uid': user[1]['uid'][0].decode('utf-8'),
        'drinkBalance': int(user[1].get('drinkBalance',[b'0'])[0].decode('utf-8'))
    } for user in users]
    success = {
        'message': 'Retrieved {} users'.format(len(users)),
        'users': users
    }
    return jsonify(success), 200


@users_bp.route('/users/credits', methods=['GET'])
@check_token()
def get_credits():
    uid = request.args.get('uid', None)
    if uid is None:
        return bad_params('Please provide a valid CSH uid as a URI parameter.')
    try:
        user = _ldap.get_member(uid, uid=True)
    except KeyError:
        return bad_params('The requested uid \'{}\' does not belong to any user.'.format(uid))
    user_ret = {
        'uid': user.uid,
        'cn': user.cn,
        'drinkBalance': user.drinkBalance
    }
    success = {
        'message': 'Retrieved user with uid \'{}\''.format(uid),
        'user': user_ret
    }
    return jsonify(success), 200


@users_bp.route('/users/credits', methods=['PUT'])
@check_token(admin_only=True)
def manage_credits():
    if request.headers.get('Content-Type') != 'application/json':
        return bad_headers_content_type()

    body = request.json

    unprovided = []
    if 'drinkBalance' not in body:
        unprovided.append('drinkBalance')
    if 'uid' not in body:
        unprovided.append('uid')

    if len(unprovided) > 0 :
        return bad_params('The following required parameters were not provided: {}'.format(', '.join(unprovided)))

    try:
        old_balance, new_balance = _manage_credits(body['uid'], body['drinkBalance'])
    except ValueError:
        return bad_params('The new drinkBalance must be an integer')
    except KeyError:
        return bad_params('The requested uid \'{}\' does not belong to any user.'.format(uid))

    success = {
        'message': 'Drink balance updated from {} credits to {} credits for user \'{}\''.format(
                        old_balance,
                        new_balance,
                        body['uid']
                    ),
    }

    return jsonify(success), 200

def _get_credits(uid):
    user = _ldap.get_member(uid, uid=True)
    return int(user.drinkBalance)

def _manage_credits(uid, drinkBalance):
    """ Set the drinkBalance of the user corresponding to the provided uid """
    i_balance = int(drinkBalance)
    user = _ldap.get_member(uid, uid=True)

    old_drinkBalance = user.drinkBalance
    dn = 'uid={},cn=users,cn=accounts,dc=csh,dc=rit,dc=edu'.format(uid)

    m_old_balance = {'drinkBalance': [user.drinkBalance.encode('utf-8')]}
    m_new_balance = {'drinkBalance': [str(drinkBalance).encode('utf-8')]}

    modlist = ldap.modlist.modifyModlist(m_old_balance, m_new_balance)
    ldap_conn = _ldap.get_con()
    ldap_conn.modify_s(dn, modlist)

    user = _ldap.get_member(uid, uid=True)
    return int(old_drinkBalance), int(user.drinkBalance)

