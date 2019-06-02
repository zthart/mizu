from abc import ABC, abstractmethod

class DataAdapterABC(ABC):

    @abstractmethod
    def get_machine(self, machine_id):
        """ Get a machine object with the provided ID """
        pass

    @abstractmethod
    def get_machines(self):
        """ Get all machine objects present in the system """
        pass

    @abstractmethod
    def get_items(self):
        """ Get all items present in the system """
        pass
    
    @abstractmethod
    def get_item(self, item_id):
        """ Get the item corresponding to the provided ID """
        pass

    @abstractmethod
    def create_item(self, item_name, item_price):
        """ Create an item provided a name and price """
        pass

    @abstractmethod
    def delete_item(self, item_id):
        """ Delete the item with the provided ID """
        pass

    @abstractmethod
    def update_item(self, item_id, item_name=None, item_price=None):
        """ Update the name and/or price of the item with the provided ID """
        pass

    @abstractmethod
    def update_slot_status(self, machine_id, slot_num):
        """ Update the status (enabled/disabled) of the numbered slot in the machine with the provided ID """
        pass

