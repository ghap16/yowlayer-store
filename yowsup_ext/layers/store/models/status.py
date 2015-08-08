from yowsup_ext.layers.store import db
import peewee
import datetime
class Status(db.get_base_model()):
    text = peewee.TextField()
    created = peewee.DateTimeField(default=datetime.datetime.now())