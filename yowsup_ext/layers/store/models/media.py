from yowsup_ext.layers.store import db
import peewee
from mediatype import MediaType

class Media(db.get_base_model()):
    type = peewee.ForeignKeyField(MediaType)
    preview = peewee.CharField()
    remote_url = peewee.CharField()
    local_path = peewee.CharField(null = True)
    data = peewee.BlobField(null = True)
    transfer_status = peewee.IntegerField(default=0)
    size = peewee.IntegerField()