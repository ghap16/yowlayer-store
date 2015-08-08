from yowsup_ext.layers.store import db
import peewee
import datetime
from contact import Contact
from group import Group
from broadcast import Broadcast


class Conversation(db.get_base_model()):
    contact = peewee.ForeignKeyField(Contact, null=True)
    group = peewee.ForeignKeyField(Group, null = True)
    broadcast = peewee.ForeignKeyField(Broadcast, null=True)
    created = peewee.DateTimeField(datetime.datetime.now())