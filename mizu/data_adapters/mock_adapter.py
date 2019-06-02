from . import DataAdapterABC

class MockAdapter(DataAdapterABC):
    def __init__(self):
        pass

    def get_machine(self, machine_id):
        pass

    def get_machines(self):
        pass

    def get_items(self):
        pass

    def get_item(self, item_id):
        pass

    def create_item(self, item_name, item_price):
        pass

    def delete_item(self, item_id):
        pass

    def update_item(self, item_id, item_name=None, item_price=None):
        pass

    def update_slot_status(self, machine_id, slot_num):
        pass

