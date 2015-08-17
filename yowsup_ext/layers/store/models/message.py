from yowsup_ext.layers.store import db
from yowsup.layers.protocol_messages.protocolentities.message import MessageProtocolEntity
import peewee
import datetime

from conversation import Conversation
from media import Media
from state import State

class Message(db.get_base_model()):
    id_gen = peewee.CharField(null=False, unique=True)
    conversation = peewee.ForeignKeyField(Conversation)
    created = peewee.DateTimeField(default=datetime.datetime.now())
    t_sent = peewee.DateTimeField(default=datetime.datetime.now())
    content = peewee.TextField(null=True)
    media = peewee.ForeignKeyField(Media, null=True)

    def getMediaType(self):
        if self.media is not None:
            return self.media.type

    def getState(self):
        from messagestate import MessageState
        return MessageState.get_state(self)

    @classmethod
    def getByState(cls, states, conversation = None):
        from messagestate import MessageState

        query = (cls.select()
                .join(MessageState)
                .join(State))
        if conversation:
            query = query.where(State.id << [state.id for state in states], Message.conversation == conversation)
        else:
            query = query.where(State.id << [state.id for state in states])

        return query

    def toDict(self):
        return {
            "id": self.id_gen,
            "conversation": self.conversation.toDict(),
            "created": self.created,
            "content": self.content,
            "t_sent": self.t_sent,
            "type": MessageProtocolEntity.MESSAGE_TYPE_TEXT if self.media is None else MessageProtocolEntity.MESSAGE_TYPE_MEDIA,
            "media": self.media.toDict() if self.media is not None else None,
            "state": self.getState().name
        }
