""" Adapter for a in-memory dictionary based storage backend
"""

from functools import wraps

from mizu import mock_db

from . import DataAdapterABC


def check_dataset(func):
    ''' Simple decorator to make sure that calls to the mock adapter when no mock data is present don't explode. '''
    @wraps(func)
    def wrapped_function(*args, **kwargs):
        if mock_db is None:
            raise ValueError('No mock dataset was found at app start, mocking is disabled')

        return func(*args, **kwargs)
    return wrapped_function

# pylint: disable=missing-function-docstring
class MockAdapter(DataAdapterABC):
    """ Adapter for an in-memory dataset filled with fake data, useful for mocking higher-privileged requests """
    @staticmethod
    @check_dataset
    def get_machine(machine_name):
        r_machine = None
        for machine in mock_db['Machines']:
            if machine['name'] == machine_name:
                r_machine = machine
                break

        return r_machine

    @staticmethod
    @check_dataset
    def get_machines():
        return mock_db['Machines']

    @staticmethod
    @check_dataset
    def get_items():
        return mock_db['Items']

    @staticmethod
    @check_dataset
    def get_item(item_id):
        r_item = None
        for item in mock_db['Items']:
            if item['id'] == item_id:
                r_item = item
                break

        return r_item

    @staticmethod
    @check_dataset
    def create_item(item_name, item_price):
        item_ids = [item['id'] for item in mock_db['Items']]
        item_ids.sort(reverse=True)

        latest_id = item_ids[0]
        new_item = {'id': latest_id+1, 'name': item_name, 'price': item_price}
        mock_db['Items'].append(new_item)
        return new_item

    @staticmethod
    @check_dataset
    def delete_item(item_id):
        for idx, item in enumerate(mock_db['Items']):
            if item['id'] == item_id:
                del mock_db['Items'][idx]
                return True

        return False

    @staticmethod
    @check_dataset
    def update_item(item_id, item_name=None, item_price=None):
        update_idx = None
        for idx, item in enumerate(mock_db['Items']):
            if item['id'] == item_id:
                update_idx = idx
                break

        if update_idx is None:
            raise ValueError('The ID provided does not correspond to an item in the system.')

        if item_name:
            mock_db['Items'][update_idx]['name'] = item_name
        if item_price:
            mock_db['Items'][update_idx]['price'] = item_price

        return mock_db['Items'][update_idx]

    @staticmethod
    @check_dataset
    def get_slots_in_machine(machine_name):
        machine = MockAdapter.get_machine(machine_name)
        if machine is None:
            raise ValueError('The Machine name provided did not correspond to any known machine.')

        list_slots = []
        for slot in mock_db['Slots']:
            if slot['machine'] == machine['id']:
                list_slots.append(slot)

        return list_slots

    @staticmethod
    def update_slot_status(machine_id, slot_num):
        pass


    @staticmethod
    @check_dataset
    def get_user(uid=None):
        if uid is None:
            return mock_db['Users']
        else:
            for user in mock_db['Users']:
                if user['uid'] == uid:
                    return user

            # Using Keyerror to maintain compat with CSH Ldap Lib
            raise KeyError('The requested user does not exist')

    @staticmethod
    @check_dataset
    def update_user_balance(uid, balance):
        for user in mock_db['Users']:
            if user['uid'] == uid:
                old_balance = user['drinkBalance']
                user['drinkBalance'] = balance
                return int(old_balance), int(balance)
        # Using KeyError to maintain compat with CSH Ldap Lib
        raise KeyError('The request user does not exist')
