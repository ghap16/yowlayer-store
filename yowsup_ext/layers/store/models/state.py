from yowsup_ext.layers.store import db
import peewee
class State(db.get_base_model()):
    name = peewee.CharField()