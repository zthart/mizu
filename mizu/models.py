from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Text
from sqlalchemy import Boolean

from mizu import db


class Machine(db.Model):
    __tablename__ = 'machines'

    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True, nullable=False)
    display_name = Column(Text, server_default="New Machine", nullable=False)

    def __init__(self, name, display_name):
        self.name = name
        self.display_name = display_name


class Item(db.Model):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    price = Column(Integer, nullable=False)

    def __init__(self, name, price):
        self.name = name
        self.price = price


class Slot(db.Model):
    __tablename__ = 'slots'

    machine = Column(ForeignKey('machines.id'), primary_key=True)
    number = Column(Integer, primary_key = True)
    item = Column(ForeignKey('items.id'), nullable=True)
    active = Column(Boolean, default=False, server_default="false", nullable=False)
    count = Column(Integer, nullable=True)

    def __init__(self, machine, number):
        self.machine = machine
        self.number = number

class Log(db.Model):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True)
    machine = Column(ForeignKey('machines.id'), nullable=False)
    item = Column(ForeignKey('items.id'), nullable=False)
    user = Column(Text, nullable=False)
    time = Column(DateTime, nullable=False)

    def __init__(self, machine, item, user, time):
        self.machine = machine
        self.item = item
        self.user = user
        self.time = time

class Temp(db.Model):
    __tablename__ = 'temps'

    machine = Column(ForeignKey('machines.id'), primary_key=True)
    time = Column(DateTime, primary_key=True)
    temp = Column(Float, nullable=False)

    def __init__(self, machine, time, temp):
        self.machine = machine
        self.time = time
        self.temp = temp

