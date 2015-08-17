from yowsup_ext.layers.store import db
import peewee
import datetime
from contact import Contact
from group import Group
from broadcast import Broadcast

TYPE_CONTACT    = "contact"
TYPE_GROUP      = "group"
TYPE_BROADCAST  = "broadcast"

class Conversation(db.get_base_model()):
    contact = peewee.ForeignKeyField(Contact, null=True)
    group = peewee.ForeignKeyField(Group, null = True)
    broadcast = peewee.ForeignKeyField(Broadcast, null=True)
    created = peewee.DateTimeField(default=datetime.datetime.now())

    def getType(self):
        if self.contact:
            return TYPE_CONTACT

        if self.group:
            return TYPE_GROUP

        if self.broadcast:
            return TYPE_BROADCAST

    def toDict(self):
        return {
            "contact": self.contact.toDict() if self.contact else None,
            "group": self.group.toDict() if self.group else None,
            "broadcast": self.broadcast.toDict() if self.broadcast else None,
            "type": self.getType(),
            "created": self.created
        }
