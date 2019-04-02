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

from mizu.errors import bad_params

from mizu import app

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
    pass

