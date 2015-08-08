from yowsup_ext.layers.store import db
import peewee
import datetime

from conversation import Conversation
from media import Media


class Message(db.get_base_model()):
    conversation = peewee.ForeignKeyField(Conversation)
    created = peewee.DateTimeField(datetime.datetime.now())
    t_sent = peewee.DateTimeField()
    content = peewee.TextField()
    media = peewee.ForeignKeyField(Media, null=True)