""" Mizu - drinks.py

/drinks
/drinks/drop

Routes for retrieving information on the contents of the machines, and dropping drinks
"""

from flask import Blueprint, jsonify, request

from mizu import db

from mizu.models import Machine
from mizu.models import Item
from mizu.models import Slot

from mizu.users import _manage_credits, _get_credits
from mizu.auth import check_token
from mizu.errors import bad_params, bad_headers_content_type
from mizu.data_adapters import get_adapter

from mizu import app

import requests

drinks_bp = Blueprint('drinks_bp', __name__)

@drinks_bp.route('/drinks', methods=['GET'])
@get_adapter
@check_token()
def current_drinks(adapter):
    # optional request paremeter, the name of the machine to get stock information
    machine_name = request.args.get('machine', None)

    # assemble an array of (id, name) tuples
    if machine_name is None:
        machines = adapter.get_machines()
    else:
        # We're given a machine name
        machine = adapter.get_machine(machine_name)

        if machine is None:
            return bad_params('The provided machine name \'{}\' is not a valid machine'.format(machine_name))

        machines = []
        machines.append(machine)

    response = {
        "machines": []
    } 

    for machine in machines:
        machine_slots = adapter.get_slots_in_machine(machine['name'])
        
        is_online = True
        
        try:
            slot_status = _get_machine_status(machine['name'])
        except requests.exceptions.ConnectionError:
            slot_status = [{'empty': True} for n in range(len(machine_slots))]
            is_online = False  # seems a useful feature
        
        machine_contents = {
            'id': machine['id'], 
            'name': machine['name'], 
            'display_name': machine['display_name'],
            'is_online': is_online,
            'slots': []
        }

        for slot in machine_slots:
            slot_item = adapter.get_item(slot['item'])
            machine_contents['slots'].append({
                "number": slot['number'],
                "active": slot['active'],
                "empty": slot_status[slot['number']-1]['empty'],
                "item": {
                    "name": slot_item['name'],
                    "price": slot_item['price'],
                    "id": slot_item['id'],
                },

            })
        response['machines'].append(machine_contents)

    response['message'] = 'Successfully retrieved machine contents for {}'.format(
        ', '.join([machine['name'] for machine in machines])
    )

    return jsonify(response), 200


@drinks_bp.route('/drinks/drop', methods=['POST'])
@check_token(return_user_obj=True)
def drop_drink(user = None):
    if request.headers.get('Content-Type') != 'application/json':
        return bad_headers_content_type()

    bal_before = _get_credits(user['preferred_username'])

    body = request.json

    unprovided = []
    if 'machine' not in body:
        unprovided.append('machine')
    if 'slot' not in body:
        unprovided.append('slot')

    if len(unprovided) > 0:
        return bad_params('The following required parameters were not provided: {}'.format(
            ', '.join(unprovided)
        ))

    machine = db.session.query(Machine).filter(Machine.name == body['machine']).first()
    if machine is None:
        return bad_params('The machine name \'{}\' is not a valid machine'.format(body['machine']))

    slot = db.session.query(Slot).filter(Slot.number == body['slot'], Slot.machine == machine.id).first()
    if slot is None:
        return bad_params('The machine \'{}\' does not have a slot with id \'{}\''.format(
            body['machine'],
            body['slot']
        ))

    slot_status = _get_machine_status(body['machine'])
    if slot_status[body['slot']-1]['empty']:  # slots are 1 indexed
        return jsonify({
            "error": "The requested slot is empty!",
            "errorCode": 400
        }), 400

    item = db.session.query(Item).filter(Item.id == slot.item).first()

    if bal_before < item.price:
        response = {
            "error": "The user \'{}\' does not have a sufficient drinkBalance",
            "errorCode": 402
        }
        return jsonify(response), 402

    machine_hostname = '{}.csh.rit.edu'.format(machine.name)
    request_endpoint = 'https://{}/drop'.format(machine_hostname)
    
    body = {
        "slot": slot.number
    }

    headers = {
        'X-Auth-Token': app.config['MACHINE_API_TOKEN'],
        'Content-Type': 'application/json'
    }

    # Do the thing
    try:
        response = requests.post(request_endpoint, json=body, headers=headers)
    except requests.exceptions.ConnectionError:
        return jsonify({
            "error": "Could not contact drink machine for drop!",
            "errorCode": 500
        }), 500

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        return jsonify({"error": "Could not access slot for drop!",
                        "message": response.json()['error'],
                        "errorCode": response.status_code}),\
                       response.status_code

    new_balance = bal_before - item.price
    _manage_credits(user['preferred_username'], new_balance)

    return jsonify({"message": "Drop successful!", "drinkBalance": new_balance}), response.status_code

def _get_machine_status(machine_name):
    """ helper function to query a machine given it's name (should be the actual hostname, will be dropped into a
        {}.csh.rit.edu template), and return slot status information in a more programmatically useful way.

        Realistically, the data should look like this coming back from the mahcine -- this is low hanging fruit for someone
        to fix.

        Warning::

            This doesn't actually validate the machine name. That should be done in what ever route needs to call this function.

        Raises:
            requests.exceptions.HTTPError: in the event the machine responds with a non-2XX
    """

    headers = {
        'X-Auth-Token': app.config['MACHINE_API_TOKEN'],
        'Content-Type': 'application/json'
    }

    endpoint = 'https://{}.csh.rit.edu/health'.format(machine_name)

    health_status = requests.get(endpoint, headers=headers)
    health_status.raise_for_status()

    health_results = health_status.json()

    slots = []

    for idx, slot in enumerate(health_results['slots'], 1):
        slots.append({
            'number': idx,
            'w1id': slot.split('(')[1].split(')')[0],
            'empty': 'empty' in slot
        })

    return slots

