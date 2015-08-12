from yowsup_ext.layers.store import db
import peewee
from message import Message
from state import State
from contact import Contact

class MessageState(db.get_base_model()):
    message = peewee.ForeignKeyField(Message)
    state = peewee.ForeignKeyField(State)
    contact = peewee.ForeignKeyField(Contact, null=True)

    @classmethod
    def set_received(cls, message):
        messageState = MessageState(message = message, state = State.get_received())
        messageState.save()

    @classmethod
    def set_sent(cls, message):
        messageState = MessageState.get_or_create(message = message, state = State.get_sent_queued())[0]
        messageState.state = State.get_sent()
        messageState.save()

    @classmethod
    def set_sent_queued(cls, message):
        messageState = MessageState(message = message, state = State.get_sent_queued())
        messageState.save()

    @classmethod
    def set_sent_delivered(cls, message, contact = None):
        pass

    @classmethod
    def set_sent_read(cls, message, contact = None):
        pass