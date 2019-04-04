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

from mizu.errors import bad_params, bad_headers_content_type

from mizu import app

import requests

drinks_bp = Blueprint('drinks_bp', __name__)

@drinks_bp.route('/drinks', methods=['GET'])
def current_drinks():
    # optional request paremeter, the name of the machine to get stock information
    machine_name = request.args.get('machine', None)

    # assemble an array of (id, name) tuples
    if machine_name is None:
        machines = db.session.query(Machine).all()
        machines = [(machine.id, machine.name) for machine in machines]
    else:
        # We're given a machine name
        machine = db.session.query(Machine).filter(Machine.name == machine_name).first()

        if machine is None:
            return bad_params('The provided machine name \'{}\' is not a valid machine'.format(machine_name))

        machines = []
        machines.append((machine.id, machine.name))

    response = {
        "machines": {}
    }
    for machine in machines:
        machine_slots = db.session.query(Slot).filter(Slot.machine == machine[0]).all()
        machine_contents = {}
        for slot in machine_slots:
            slot_item = db.session.query(Item).filter(Item.id == slot.item).first()
            machine_contents[str(slot.number)] = {
                "name": slot_item.name,
                "price": slot_item.price,
                "id": slot_item.id,
            }
        response['machines'].update({machine[1]: machine_contents})

    response['message'] = 'Successfully retrieved machine contents for {}'.format(
        ', '.join([machine[1] for machine in machines])
    )

    return jsonify(response), 200

@drinks_bp.route('/drinks/drop', methods=['POST'])
def drop_drink():
    if request.headers.get('Content-Type') != 'application/json':
        return bad_headers_content_type()

    body  = request.json

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
    response = requests.post(request_endpoint, json=body, headers=headers)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        return jsonify({"error": "Could not access slot for drop!", "errorCode": response.status_code}),\
                       response.status_code

    return jsonify({"message": "Drop successful!"}), response.status_code

