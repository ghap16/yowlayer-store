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
    def get_state(cls, message):
        try:
            return MessageState.get(message = message).state
        except peewee.DoesNotExist:
            return None

    @classmethod
    def update_received_state(cls, message, state):
        try:
            mstate = MessageState.get(message=message)
        except peewee.DoesNotExist:
            mstate = MessageState(message=message)
        mstate.state = state
        mstate.save()

    @classmethod
    def set_received(cls, message):
        cls.update_received_state(message, State.get_received())

    @classmethod
    def set_received_read_remote(cls, message):
        cls.update_received_state(message, State.get_received_read_remote())

    @classmethod
    def set_received_read(cls, message):
        cls.update_received_state(message, State.get_received_read())

    @classmethod
    def set_received_remote(cls, message):
        cls.update_received_state(message, State.get_received_remote())

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
        if contact:
            messageState = MessageState.get(message = message, contact = contact)
        else:
            messageState = MessageState.get(message = message)
        messageState.state = State.get_sent_delivered()
        messageState.save()

    @classmethod
    def set_sent_read(cls, message, contact = None):
        if contact:
            messageState = MessageState.get(message = message, contact = contact)
        else:
            messageState = MessageState.get(message = message)
        messageState.state = State.get_sent_read()
        messageState.save()
