from yowsup_ext.layers.store import db
import peewee
import datetime

from conversation import Conversation
from media import Media


class Message(db.get_base_model()):
    id_gen = peewee.CharField(null=False, unique=True)
    conversation = peewee.ForeignKeyField(Conversation)
    created = peewee.DateTimeField(default=datetime.datetime.now())
    t_sent = peewee.DateTimeField(default=datetime.datetime.now())
    content = peewee.TextField()
    media = peewee.ForeignKeyField(Media, null=True)
