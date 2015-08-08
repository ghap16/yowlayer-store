from yowsup_ext.layers.store import db
import peewee
import datetime

class Broadcast(db.get_base_model()):
    wId = peewee.CharField() #Can't remember so far what that was for, but it's in openwa so maybe important
    created = peewee.DateTimeField(default=datetime.datetime.now())