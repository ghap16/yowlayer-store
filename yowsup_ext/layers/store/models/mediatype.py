from yowsup_ext.layers.store import db
import peewee

class MediaType(db.get_base_model()):
    type = peewee.CharField()