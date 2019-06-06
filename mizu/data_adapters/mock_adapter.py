from . import DataAdapterABC

from mizu import mock_db

from mizu.models import Item
from mizu.models import Machine
from mizu.models import Slot

class MockAdapter(DataAdapterABC):

    @staticmethod
    def get_machine(machine_name):
        if mock_db is None:
            raise ValueError('No mock dataset was found at app start, mocking is disabled')

        r_machine = None
        for machine in mock_db['Machines']:
            if machine['name'] == machine_name:
                r_machine = machine
                break

        return r_machine

    @staticmethod
    def get_machines():
        if mock_db is None:
            raise ValueError('No mock dataset was found at app start, mocking is disabled')

        return mock_db['Machines']

    @staticmethod
    def get_items():
        if mock_db is None:
            raise ValueError('No mock dataset was found at app start, mocking is disabled')
        return mock_db['Items']

    @staticmethod
    def get_item(item_id):
        if mock_db is None:
            raise ValueError('No mock dataset was found at app start, mocking is disabled')
        
        r_item = None
        for item in mock_db['Items']:
            if item['id'] == item_id:
                r_item = item
                break

        return r_item
    
    @staticmethod
    def create_item(item_name, item_price):
        if mock_db is None:
            raise ValueError('No mock dataset was found at app start, mocking is disabled')
        
        item_ids = [item['id'] for item in mock_db['Items']]
        item_ids.sort(reverse=True)

        latest_id = item_ids[0]
        new_item = {'id': latest_id+1, 'name': item_name, 'price': item_price}
        mock_db['Items'].append(new_item)
        return new_item
    
    @staticmethod
    def delete_item(item_id):
        if mock_db is None:
            raise ValueError('No mock dataset was found at app start, mocking is disabled')

        for idx, item in enumerate(mock_db['Items']):
            if item['id'] == item_id:
                del mock_db['Items'][idx]
                return True

        return False

    @staticmethod
    def update_item(item_id, item_name=None, item_price=None):
        if mock_db is None:
            raise ValueError('No mock dataset was found at app start, mocking is disabled')

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
    def get_slots_in_machine(machine_name):
        if mock_db is None:
            raise ValueError('No mock dataset was found at app start, mocking is disabled')

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

