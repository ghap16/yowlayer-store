from yowsup_ext.layers.store import db
import peewee
import datetime
from contact import Contact

class Group(db.get_base_model()):
    jid = peewee.CharField(null=False)
    picture = peewee.BlobField(null=True)
    subject = peewee.CharField(null=True)
    subject_owner_id = peewee.ForeignKeyField(Contact, null=True)
    subject_time = peewee.DateTimeField(null=True)
    created = peewee.DateTimeField(default=datetime.datetime.now())