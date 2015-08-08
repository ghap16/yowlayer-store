from store import db
import peewee
import datetime
from contact import Contact

class Group(db.get_base_model()):
    jid = peewee.CharField()
    picture = peewee.BlobField()
    subject = peewee.CharField()
    subject_owner_id = peewee.ForeignKeyField(Contact)
    subject_time = peewee.DateTimeField()
    created = peewee.DateTimeField(default=datetime.datetime.now())