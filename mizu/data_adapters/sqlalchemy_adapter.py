from . import DataAdapterABC

from mizu import db

from mizu.models import Item
from mizu.models import Machine
from mizu.models import Slot

from sqlalchemy import orm

class SqlAlchemyAdapter(DataAdapterABC):

    @staticmethod
    def get_machines(machine_id):
        pass

    @staticmethod
    def get_machines():
        pass

    @staticmethod 
    def get_items():
        """ Query the SQL Alchemy Connected DB for All Items. 

        Returns:
            list: a list of ``Item`` objects serialized as json
        """
        db_items = db.session.query(Item).all()
        list_items = []
        for item in db_items:
            list_items.append(SqlAlchemyAdapter._serialize_to_json(item))
        
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
            return SqlAlchemyAdapter._serialize_to_json(item)

    @staticmethod
    def create_item(item_name, item_price):
        """ Create an item via the ORM 

        Returns:
            dict: An ``Item`` object serialized as json
        """
        new_item = Item(name=item_name, price=item_price)
        db.session.add(new_item)
        db.session.commit()

        return SqlAlchemyAdapter._serialize_to_json(new_item)

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
    def update_slot_status(machine_id, slot_num):
        pass

    ###########################################################################
    # Private / Helper functions

    @staticmethod
    def _serialize_to_json(item):
        """ Serialize a ``mizu.models.Item`` into a python dict / JSON """ 
        return {
            'id': item.id,
            'name': item.name,
            'price': item.price
        }
    
    @staticmethod
    def _get_item(item_id):
        """ Get a ``mizu.models.Item`` object by ID """
        return db.session.query(Item).filter(Item.id == item_id).first()

