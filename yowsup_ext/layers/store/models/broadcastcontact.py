from yowsup_ext.layers.store import db
import peewee
from contact import Contact
from broadcast import Broadcast

class BroadcastContact(db.get_base_model()):
    contact = peewee.ForeignKeyField(Contact)
    broadcast = peewee.ForeignKeyField(Broadcast)