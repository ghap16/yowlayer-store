from yowsup_ext.layers.store import db
import peewee
from mediatype import MediaType

class Media(db.get_base_model()):
    type = peewee.ForeignKeyField(MediaType)
    preview = peewee.CharField()
    remote_url = peewee.CharField(null = True)
    local_path = peewee.CharField(null = True)
    data = peewee.TextField(null = True)
    transfer_status = peewee.IntegerField(default=0)
    size = peewee.IntegerField(null=True)
    mimetype = peewee.CharField(null=True)
    filehash = peewee.CharField(null=True)
    filename = peewee.CharField(null=True)
    encoding = peewee.CharField(null=True)
