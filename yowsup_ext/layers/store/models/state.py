from yowsup_ext.layers.store import db
import peewee

STATE_RECEIVED              = "received"                #received
STATE_RECEIVED_REMOTE       = "received_remote"         #set when delivered receipt was acked
STATE_RECEIVED_READ         = "received_read"           #set when send read receipt
STATE_RECEIVED_READ_REMOTE  = "received_read_remote"    #set when read receipt was acked
STATE_SENT_QUEUED           = "sent_queued"
STATE_SENT                  = "sent"
STATE_SENT_DELIVERED        = "sent_delivered"
STATE_SENT_READ             = "sent_read"

class State(db.get_base_model()):
    name = peewee.CharField(unique=True)

    @classmethod
    def init(cls):
        cls.get_or_create(name = STATE_RECEIVED)
        cls.get_or_create(name = STATE_RECEIVED_REMOTE)
        cls.get_or_create(name = STATE_RECEIVED_READ)
        cls.get_or_create(name = STATE_RECEIVED_READ_REMOTE)
        cls.get_or_create(name = STATE_SENT_QUEUED)
        cls.get_or_create(name = STATE_SENT)
        cls.get_or_create(name = STATE_SENT_DELIVERED)
        cls.get_or_create(name = STATE_SENT_READ)

    def __unicode__(self):
        return self.name

    @classmethod
    def get_received_read(cls):
        return cls.get(State.name == STATE_RECEIVED_READ)

    @classmethod
    def get_received_read_remote(cls):
        return cls.get(State.name == STATE_RECEIVED_READ_REMOTE)

    @classmethod
    def get_received(cls):
        return cls.get(State.name == STATE_RECEIVED)

    @classmethod
    def get_received_remote(cls):
        return cls.get(State.name == STATE_RECEIVED_REMOTE)

    @classmethod
    def get_sent_queued(cls):
        return cls.get(State.name == STATE_SENT_QUEUED)

    @classmethod
    def get_sent(cls):
        return cls.get(State.name == STATE_SENT)

    @classmethod
    def get_sent_delivered(cls):
        return cls.get(State.name == STATE_SENT_DELIVERED)

    @classmethod
    def get_sent_read(cls):
        return cls.get(State.name == STATE_SENT_READ)
