from yowsup_ext.layers.store import db
import peewee
from mediatype import MediaType

class Media(db.get_base_model()):
    type = peewee.ForeignKeyField(MediaType)
    preview = peewee.BlobField(null=True)
    remote_url = peewee.CharField(null = True)
    local_path = peewee.CharField(null = True)
    data = peewee.TextField(null = True)
    transfer_status = peewee.IntegerField(default=0)
    size = peewee.IntegerField(null=True)
    mimetype = peewee.CharField(null=True)
    filehash = peewee.CharField(null=True)
    filename = peewee.CharField(null=True)
    encoding = peewee.CharField(null=True)

    def toDict(self):
        media = {
            "type": self.type.name,
            "preview": self.preview,
            "remote_url": self.remote_url,
            "local_path": self.local_path,
            "data": self.data,
            "transfer_status": self.transfer_status,
            "size": self.size,
            "mimetype": self.mimetype,
            "filehash": self.filehash,
            "filename": self.filename,
            "encoding": self.encoding
        }
