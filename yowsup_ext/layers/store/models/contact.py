from yowsup_ext.layers.store import db
import peewee

class Contact(db.get_base_model()):
    number = peewee.CharField(unique=False, null = True)
    jid = peewee.CharField(null=False, unique=False)
    last_seen_on = peewee.DateTimeField(null=True)
    status = peewee.CharField(null=True)
    push_name = peewee.CharField(null=True)
    name = peewee.CharField(null=True)
    picture = peewee.BlobField(null=True)

    def toDict(self):
        return {
            "number": self.number,
            "jid": self.jid,
            "last_seen_on": self.last_seen_on,
            "status": self.status,
            "push_name": self.push_name,
            "name": self.name,
            "picture": self.picture
        }
