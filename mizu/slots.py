""" Mizu - slots.py

/slots

Routes for managing slots
"""

from flask import Blueprint, jsonify, request

from mizu import db

from mizu.models import Machine
from mizu.models import Slot
from mizu.models import Item

from mizu.auth import check_token
from mizu.errors import bad_params, bad_headers_content_type

from mizu import logger
from mizu import app

slots_bp = Blueprint('slots_bp', __name__)

@slots_bp.route('/slots', methods=['PUT'])
@check_token(admin_only=True)
def update_slot_status():
    if request.headers.get('Content-Type') != 'application/json':
        return bad_headers_content_type()

    body = request.json

    logger.debug('Handling slot update')

    unprovided = []
    if 'machine' not in body:
        unprovided.append('machine')
    if 'slot' not in body:
        unprovided.append('slot')

    if len(unprovided) > 0:
        return bad_params('The following required parameters were not provided: {}'.format(
            ', '.join(unprovided)
        ))

    if 'active' not in body and 'item_id' not in body:
        return bad_params('Either the state or item within a slot must be provided for an update.')

    updates = {}

    if 'active' in body:
        if not isinstance(body['active'], bool):
            return bad_params('The active parameter must be a boolean value')

        updates['active'] = body['active']

    if 'item_id' in body:
        try:
            item_id = int(body['item_id'])
            if item_id <= 0:
                raise ValueError()
        except ValueError:
            return bad_params('The item ID value must be a positive integer')

        updates['item'] = item_id

        item = db.session.query(Item).filter(Item.id == item_id).first()

        if item is None:
            return bad_params('No item with ID {} is present in the system'.format(item_id))

    try:
        slot_num = int(body['slot'])

        if slot_num <= 0:
            raise ValueError()
    except ValueError:
        return bad_params('The slot number must be a positive integer')

    machine = db.session.query(Machine).filter(Machine.name == body['machine']).first()
    if machine is None:
        return bad_params('The machine \'{}\' is not a valid machine'.format(body['machine']))

    slot = db.session.query(Slot).filter(Slot.number == slot_num, Slot.machine == machine.id).first()
    if slot is None:
        return bad_params('The machine \'{}\' does not have a slot number {}'.format(
            body['machine'],
            body['slot'],
        ))

    logger.debug('Slot update details validated')

    slot = db.session.query(Slot).filter(Slot.number == body['slot'], Slot.machine == machine.id).\
            update(updates, synchronize_session=False)

    if slot < 1:
        return jsonify({'error': 'Could not update slot', 'errorCode': 500, 'message': 'Contact a drink admin'}), 500

    db.session.commit()

    slot = db.session.query(Slot).filter(Slot.number == slot_num, Slot.machine == machine.id).first()

    success = {
        'message': 'Successfully updated slot {} in {}'.format(slot.number, body['machine']),
        'slot': {
            'machine': body['machine'],
            'number': slot.number,
            'active': slot.active,
            'item_id': slot.item,
        },
    }

    return jsonify(success), 200


