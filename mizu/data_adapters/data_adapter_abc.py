from abc import ABC, abstractmethod

class DataAdapterABC(ABC):

    @staticmethod
    @abstractmethod
    def get_machine(machine_id):
        """ Get a machine object with the provided ID """
        pass

    @staticmethod
    @abstractmethod
    def get_machines():
        """ Get all machine objects present in the system """
        pass

    @staticmethod
    @abstractmethod
    def get_items():
        """ Get all items present in the system """
        pass

    @staticmethod
    @abstractmethod
    def get_item(item_id):
        """ Get the idem with the corresponding id, if present """
        pass

    @staticmethod
    @abstractmethod
    def create_item(item_name, item_price):
        """ Create an item provided a name and price """
        pass

    @staticmethod
    @abstractmethod
    def delete_item(item_id):
        """ Delete the item with the provided ID """
        pass

    @staticmethod
    @abstractmethod
    def update_item(item_id, item_name=None, item_price=None):
        """ Update the name and/or price of the item with the provided ID """
        pass

    @staticmethod
    @abstractmethod
    def update_slot_status(machine_id, slot_num):
        """ Update the status (enabled/disabled) of the numbered slot in the machine with the provided ID """
        pass

