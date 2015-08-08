from yowsup.layers import YowLayer
from yowsup.common.tools import StorageTools
import peewee
import db
import logging
logger = logging.getLogger(__name__)

DB_NAME = StorageTools.constructPath("yow.db")


class SqliteStorageLayer(YowLayer):
    def __init__(self):
        super(SqliteStorageLayer, self).__init__()
        self.db = peewee.SqliteDatabase(DB_NAME, threadlocals=True)
        db.set_db(self.db)
        self.db.connect()
        self.setup_models()

    def setup_models(self):
        from models import State, Message, Conversation, Contact, Group, MediaType, Media, Broadcast
        from models.messagestate import MessageState
        from models.groupcontact import GroupContact
        from models.broadcastcontact import BroadcastContact
        models = [
            State,
            Message,
            MessageState,
            Conversation,
            Contact,
            Group,
            GroupContact,
            MediaType,
            Media,
            State,
            Broadcast,
            BroadcastContact
        ]
        logger.debug("setting up models")
        self.db.create_tables(models, True)
