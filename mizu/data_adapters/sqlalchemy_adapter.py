from . import DataAdapterABC

from mizu import db

from mizu.models import Item
from mizu.models import Machine
from mizu.models import Slot

from sqlalchemy import orm

class SqlAlchemyAdapter(DataAdapterABC):

    @staticmethod
    def get_machine(machine_name):
        """ Query the SQL Alchemy connected DB for a machine with the provided name

        Returns:
            dict: a ``mizu.models.Machine`` object serialized as a python dict/json, or ``None`` if no
                such machine can be found
        """
        machine = SqlAlchemyAdapter._get_machine(machine_name)
        if machine is None:
            return machine
        else:
            return SqlAlchemyAdapter._serialize_machine(machine)

    @staticmethod
    def get_machines():
        """ Query the SQL Alchemy Connected DB for all Machines.

        Returns:
            list: a list of ``Machine`` objects serialized as json
        """
        machines = db.session.query(Machine).all()
        list_machines = []
        for machine in machines:
            list_machines.append(SqlAlchemyAdapter._serialize_machine(machine))

        return list_machines

    @staticmethod
    def get_items():
        """ Query the SQL Alchemy Connected DB for All Items.

        Returns:
            list: a list of ``Item`` objects serialized as json
        """
        db_items = db.session.query(Item).all()
        list_items = []
        for item in db_items:
            list_items.append(SqlAlchemyAdapter._serialize_item(item))

        return list_items

    @staticmethod
    def get_item(item_id):
        """ Query for the item with the provided ID

        Returns:
            dict: the ``item`` serialized to json, ``None`` if no item was found
        """
        item = SqlAlchemyAdapter._get_item(item_id)
        if item is None:
            return item
        else:
            return SqlAlchemyAdapter._serialize_item(item)

    @staticmethod
    def create_item(item_name, item_price):
        """ Create an item via the ORM

        Returns:
            dict: An ``Item`` object serialized as json
        """
        new_item = Item(name=item_name, price=item_price)
        db.session.add(new_item)
        db.session.commit()

        return SqlAlchemyAdapter._serialize_item(new_item)

    @staticmethod
    def delete_item(item_id):
        """ Delete an item present in the system

        Returns:
            bool: ``True`` if the deletion was sucessful, ``False`` otherwise
        """
        item = SqlAlchemyAdapter._get_item(item_id)
        if item is None:
            return False
        db.session.delete(item)
        db.session.commit()
        return True

    @staticmethod
    def update_item(item_id, item_name=None, item_price=None):
        """ Update the name and/or price of the item corresponding to the provided ID

        Returns:
            dict: An ``Item`` object serialized as json

        Raises:
            ValueError: if the ID passed does not correspond to an itme in the system
        """
        item = SqlAlchemyAdapter._get_item(item_id)

        if item is None:
            raise ValueError('The ID provided does not represent an item in the system')

        updates = {}
        if item_name:
            updates['name'] = item_name
        if item_price:
            updates['price'] = item_price

        item = db.session.query(Item).filter(Item.id == item_id).\
                  update(updates, synchronize_session=False)
        db.session.commit()

        return SqlAlchemyAdapter.get_item(item_id)

    @staticmethod
    def get_slots_in_machine(machine_name):
        """ Retrieve a list of slot objects from a machine

        Args:
            machine_name (str): The internal name for the machine (not display name) whose items we should fetch

        Returns:
            list: a list of fully hydrated ``mizu.models.Slot`` objects serialized as python dicts / JSON

        Raises:
            ValueError: If the machine name provided does not correspond to any kown machine
        """

        results = db.session.query(Machine, Slot, Item).\
            filter(Machine.name == machine_name).\
            filter(Slot.machine == Machine.id).\
            filter(Slot.item == Item.id).\
            order_by(Slot.number.asc()).\
            all()

        slots = [SqlAlchemyAdapter._serialize_slot(s) for _, s, _ in results]
        items = [SqlAlchemyAdapter._serialize_item(i) for _, _, i in results]

        # This is side effecting - despite iterating over a zip the zip's values are references
        for slot, item in zip(slots, items):
            slot['item'] = item

        return slots

    @staticmethod
    def update_slot_status(machine_id, slot_num):
        pass

    ###########################################################################
    # Private / Helper functions

    @staticmethod
    def _serialize_item(item):
        """ Serialize a ``mizu.models.Item`` into a python dict / JSON """
        return {
            'id': item.id,
            'name': item.name,
            'price': item.price
        }

    @staticmethod
    def _serialize_machine(machine):
        """ Serialize a ``mizu.models.Machine`` into a python dict / JSON """
        return {
            'id': machine.id,
            'name': machine.name,
            'display_name': machine.display_name
        }

    @staticmethod
    def _serialize_slot(slot):
        """ Serialize a ``mizu.models.Slot`` into a python dict / JSON """
        return {
            'machine': slot.machine,
            'number': slot.number,
            'item': slot.item,
            'active': slot.active,
            'count': slot.count
        }

    @staticmethod
    def _get_item(item_id):
        """ Get a ``mizu.models.Item`` object by ID """
        return db.session.query(Item).filter(Item.id == item_id).first()

    @staticmethod
    def _get_machine(machine_name):
        """ Get a ``mizu.models.Machine`` object by name """
        return db.session.query(Machine).filter(Machine.name == machine_name).first()

