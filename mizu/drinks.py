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
from mizu import logger

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
        logger.debug('Fetching contents for machines {}'.format(', '.join([m['name'] for m in machines])))
    else:
        # We're given a machine name
        machine = adapter.get_machine(machine_name)

        if machine is None:
            err = f'The provided machine name \'{machine_name}\' is not a valid machine'
            logger.error(err)
            return bad_params(err)

        logger.debug('Fetching contents for machine {}'.format(machine_name))
        machines = []
        machines.append(machine)

    response = {
        "machines": []
    }

    for machine in machines:
        logger.debug('Querying machine details for {}'.format(machine['name']))
        machine_slots = adapter.get_slots_in_machine(machine['name'])

        is_online = True

        try:
            slot_status = _get_machine_status(machine['name'])
        except requests.exceptions.ConnectionError:
            # We couldn't connect to the machine
            logger.debug('Machine {} is unreachable, reporting as offline'.format(machine['name']))
            slot_status = [{'empty': True} for n in range(len(machine_slots))]
            is_online = False  # seems a useful feature
        except requests.exceptions.Timeout:
            # We hit a timeout waiting for the machine to respond
            logger.debug('Machine {} was reachable, but did not respond within a reasonable amount of time'.format(
                machine['name']
            ))
            slot_status = [{'empty': True} for n in range(len(machine_slots))]
            is_online = False

        machine_contents = {
            'id': machine['id'],
            'name': machine['name'],
            'display_name': machine['display_name'],
            'is_online': is_online,
            'slots': []
        }

        for slot in machine_slots:
            slot['empty'] = slot_status[slot['number']-1]['empty']
            machine_contents['slots'].append(slot)

        response['machines'].append(machine_contents)
        logger.debug('Fetched all available details for {}'.format(machine['name']))

    response['message'] = 'Successfully retrieved machine contents for {}'.format(
        ', '.join([machine['name'] for machine in machines])
    )

    return jsonify(response), 200


@drinks_bp.route('/drinks/drop', methods=['POST'])
@get_adapter
@check_token(return_user_obj=True)
def drop_drink(adapter, user = None):
    if request.headers.get('Content-Type') != 'application/json':
        return bad_headers_content_type()

    logger.debug('Handing request to drop drink')

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

    logger.debug('Drop request is valid')

    slot_status = _get_machine_status(body['machine'])
    if (body['machine'] == 'snack' and slot.count < 1) or slot_status[body['slot']-1]['empty']:  # slots are 1 indexed
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

    logger.debug('User has sufficient balance')

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
        response = requests.post(request_endpoint, json=body, headers=headers, timeout=5)
    except requests.exceptions.ConnectionError:
        return jsonify({
            "error": "Could not contact drink machine for drop!",
            "errorCode": 500
        }), 500
    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Connection to the drink machine timed out!",
            "errorCode": 500
        }), 500

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        return jsonify({"error": "Could not access slot for drop!",
                        "message": response.json()['error'],
                        "errorCode": response.status_code}),\
                       response.status_code

    logger.debug('Dropped drink - adjusting user credits')
    new_balance = bal_before - item.price
    _manage_credits(user['preferred_username'], new_balance, adapter)
    logger.debug('Credits for {} updated'.format(user['preferred_username']))

    if machine.name == 'snack':
        slot.count = Slot.count - 1 # Decrement stock count, set inactive if empty
        if slot.count == 0:
            slot.active = False
        db.session.commit()

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
            requests.exceptions.Timeout: if the machine does not respond with any bytes within 5 seconds
            requests.exceptions.ConnectionError: if the machine is not online
    """

    headers = {
        'X-Auth-Token': app.config['MACHINE_API_TOKEN'],
        'Content-Type': 'application/json'
    }

    endpoint = 'https://{}.csh.rit.edu/health'.format(machine_name)
    health_status = requests.get(endpoint, headers=headers, timeout=5)
    health_status.raise_for_status()

    health_results = health_status.json()

    logger.debug('Reached machine {} succesfully'.format(machine_name))

    slots = []

    for idx, slot in enumerate(health_results['slots'], 1):
        slots.append({
            'number': idx,
            'w1id': slot.split('(')[1].split(')')[0],
            'empty': 'empty' in slot
        })

    return slots
