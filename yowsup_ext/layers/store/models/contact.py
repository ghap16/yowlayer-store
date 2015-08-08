from yowsup_ext.layers.store import db
import peewee

class Contact(db.get_base_model()):
    number = peewee.CharField(unique=True)
    jid = peewee.CharField()
    last_seen_on = peewee.DateTimeField()
    status = peewee.CharField()
    push_name = peewee.CharField()
    name = peewee.CharField()
    source_id= peewee.CharField(null=True) #id in data source, like in phone addreess book
    picture = peewee.BlobField()