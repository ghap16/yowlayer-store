from yowsup_ext.layers.store import db
import peewee
from message import Message
from state import State
from contact import Contact

class MessageState(db.get_base_model()):
    message = peewee.ForeignKeyField(Message)
    state = peewee.ForeignKeyField(State)
    contact = peewee.ForeignKeyField(Contact, null=True)